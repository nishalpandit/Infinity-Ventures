from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.db.models import Q, Sum, Count, Avg, Prefetch
import os
import re
import mimetypes
from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.template import TemplateDoesNotExist
from .models import (
    VendorProfile, QuickService, Job, JobImage, Bid, Subscription, Category, Location, 
    UserProfile, Message, GlobalSettings, SiteBranding, HeroSection, 
    QuickServiceCard, FeaturedProjectCard, PackageCard, Testimonial, TrustMetric,
    VendorWallet, WalletTransaction, PayoutRequest, VendorKYC,
    DisputeTicket, DisputeMessage, JobCompletionProof, ServiceReview, ServiceBooking,
    BidCreditTransaction, BidPlan, CustomerAddress
)

from .review_services import submit_booking_review, ReviewError

User = get_user_model()

import json
import base64
import uuid
from datetime import datetime
from decimal import Decimal
from django.utils import timezone
from django.core.files.base import ContentFile

def get_admin_state_context(request):
    """
    Helper to extract State / Operational Territory context for Area Admin / Super Admin.
    Supports multiple admins assigned to the same state.
    """
    db_states = list(Location.objects.values_list('state', flat=True).distinct().order_by('state'))
    default_states = ['Jharkhand', 'Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'Uttar Pradesh', 'West Bengal', 'Gujarat', 'Bihar', 'Rajasthan', 'Madhya Pradesh', 'Telangana', 'Andhra Pradesh', 'Kerala', 'Punjab', 'Haryana', 'Odisha']
    available_states = sorted(list(set([s for s in (db_states + default_states) if s])))

    u = request.user
    is_area_admin = False
    admin_state = None
    co_admins = User.objects.none()

    if u.is_authenticated:
        if u.role == 'ADMIN' and not u.is_superuser:
            is_area_admin = True
            admin_state = u.assigned_state or (available_states[0] if available_states else 'Jharkhand')
            co_admins = User.objects.filter(role='ADMIN', assigned_state=admin_state).exclude(id=u.id)
        elif u.is_superuser:
            selected_state = request.GET.get('state')
            if selected_state == 'all':
                admin_state = None
                co_admins = User.objects.filter(role='ADMIN')
            elif selected_state:
                admin_state = selected_state
                co_admins = User.objects.filter(role='ADMIN', assigned_state=admin_state)
            else:
                admin_state = u.assigned_state or None
                if admin_state:
                    co_admins = User.objects.filter(role='ADMIN', assigned_state=admin_state)

    return admin_state, is_area_admin, available_states, co_admins

def is_vendor_in_state(vendor, state_name):
    """
    Checks if a vendor is present in the specified state/territory.
    Evaluates assigned_state, VendorProfile (location, address), UserProfile (state, city),
    and all registered cities for that state in Location table.
    """
    if not vendor or not state_name:
        return False
    state_lower = state_name.strip().lower()

    if vendor.assigned_state and vendor.assigned_state.strip().lower() == state_lower:
        return True

    vp = getattr(vendor, 'vendor_profile', None)
    if vp:
        if vp.location and state_lower in vp.location.lower():
            return True
        if vp.address and state_lower in vp.address.lower():
            return True

    up = getattr(vendor, 'user_profile', None)
    if up and up.state and up.state.strip().lower() == state_lower:
        return True

    cities = [c.strip().lower() for c in Location.objects.filter(state__iexact=state_name).values_list('city', flat=True) if c and c.strip()]
    if vp:
        if vp.location and any(c in vp.location.lower() for c in cities):
            return True
        if vp.address and any(c in vp.address.lower() for c in cities):
            return True
    if up and up.city and up.city.strip().lower() in cities:
        return True

    return False

def get_in_state_kyc_filter(admin_state):
    """
    Constructs an ORM Q filter to retrieve all VendorKYC records
    where the vendor is present in the specified admin_state.
    """
    if not admin_state:
        return Q()
    admin_state = admin_state.strip()
    cities = list(Location.objects.filter(state__iexact=admin_state).values_list('city', flat=True))
    q_filter = (
        Q(vendor__assigned_state__iexact=admin_state) |
        Q(vendor__vendor_profile__location__icontains=admin_state) |
        Q(vendor__vendor_profile__address__icontains=admin_state) |
        Q(vendor__user_profile__state__iexact=admin_state)
    )
    for c in cities:
        c_str = c.strip()
        if c_str:
            q_filter |= Q(vendor__vendor_profile__location__icontains=c_str)
            q_filter |= Q(vendor__vendor_profile__address__icontains=c_str)
            q_filter |= Q(vendor__user_profile__city__icontains=c_str)
    return q_filter

def is_service_in_state(service, state_name):
    """
    Checks if a QuickService is located within or provided by a vendor in the specified territory.
    """
    if not service or not state_name:
        return False
    state_lower = state_name.strip().lower()

    if service.location and service.location.state and service.location.state.strip().lower() == state_lower:
        return True

    if service.locality and state_lower in service.locality.lower():
        return True

    cities = [c.strip().lower() for c in Location.objects.filter(state__iexact=state_name).values_list('city', flat=True) if c and c.strip()]
    if service.locality and any(c in service.locality.lower() for c in cities):
        return True

    if getattr(service, 'vendor', None) and is_vendor_in_state(service.vendor, state_name):
        return True

    return False

def get_in_state_qs_filter(admin_state):
    """
    Constructs an ORM Q filter to retrieve all QuickService records
    where the service location, locality, or vendor is present in the specified admin_state.
    """
    if not admin_state:
        return Q()
    admin_state = admin_state.strip()
    cities = list(Location.objects.filter(state__iexact=admin_state).values_list('city', flat=True))
    q_filter = (
        Q(location__state__iexact=admin_state) |
        Q(locality__icontains=admin_state) |
        Q(vendor__assigned_state__iexact=admin_state) |
        Q(vendor__vendor_profile__location__icontains=admin_state) |
        Q(vendor__vendor_profile__address__icontains=admin_state) |
        Q(vendor__user_profile__state__iexact=admin_state)
    )
    for c in cities:
        c_str = c.strip()
        if c_str:
            q_filter |= Q(locality__icontains=c_str)
            q_filter |= Q(vendor__vendor_profile__location__icontains=c_str)
            q_filter |= Q(vendor__vendor_profile__address__icontains=c_str)
            q_filter |= Q(vendor__user_profile__city__icontains=c_str)
    return q_filter

def get_user_dashboard_context(user, request=None):
    name = user.get_full_name() or user.username
    initials = (user.first_name[:1].upper() + user.last_name[:1].upper()) if (user.first_name and user.last_name) else (user.first_name[:2].upper() if user.first_name else user.username[:2].upper())
    date_str = datetime.now().strftime("%A, %d %B %Y")
    
    # Resolve user's location
    u_prof = getattr(user, 'user_profile', None)
    user_city = None
    user_state = None
    if u_prof and u_prof.city:
        user_city = u_prof.city.strip()
        user_state = u_prof.state.strip() if u_prof.state else None
    
    if not user_city and request:
        user_city = request.session.get('user_city') or request.COOKIES.get('sugu_user_city')
        user_state = request.session.get('user_state') or request.COOKIES.get('sugu_user_state')

    if not user_city and getattr(user, 'assigned_city', None):
        user_city = user.assigned_city.strip()
        user_state = user.assigned_state.strip() if user.assigned_state else None

    if not user_city and hasattr(user, 'vendor_profile') and user.vendor_profile and user.vendor_profile.location:
        parts = user.vendor_profile.location.split(',')
        user_city = parts[0].strip()
        if len(parts) > 1:
            user_state = parts[1].strip()

    if not user_city:
        user_city = "Ranchi"
        user_state = "Jharkhand"

    user_location_str = f"{user_city}, {user_state}" if user_state else user_city

    # Check whether user_city is listed in Super Admin dashboard active locations
    active_cities = list(Location.objects.filter(status='active').values_list('city', flat=True))
    active_cities_lower = {c.lower().strip() for c in active_cities if c}
    is_service_available = user_city.lower().strip() in active_cities_lower

    from .models import ServiceBooking
    qs_bookings = ServiceBooking.objects.filter(customer=user)
    active_qs = qs_bookings.exclude(status__in=['completed', 'cancelled']).count()
    completed_qs = qs_bookings.filter(status='completed').count()
    
    job_list = Job.objects.filter(user=user)
    active_jobs = job_list.exclude(status__in=['completed', 'cancelled', 'closed']).count()
    completed_jobs = job_list.filter(status='completed').count()
    
    pending_bids_jobs = Bid.objects.filter(job__user=user, status__in=['submitted', 'pending']).count()
    pending_quotations = pending_bids_jobs
    
    selected_vendors_jobs = Bid.objects.filter(job__user=user, status='selected').count()
    selected_vendors = selected_vendors_jobs
    
    from .models import VendorKYC
    approved_kyc_vendor_ids = set(VendorKYC.objects.filter(status='approved').values_list('vendor_id', flat=True))

    recent_qs = qs_bookings.select_related('quick_service', 'quick_service__category', 'vendor', 'vendor__vendor_profile').order_by('-created_at')[:5]
    for b in recent_qs:
        b.selected_vendor_name = b.vendor.vendor_profile.company_name if hasattr(b.vendor, 'vendor_profile') and b.vendor.vendor_profile.company_name else (b.vendor.get_full_name() or b.vendor.username)
        b.is_vendor_verified = b.vendor_id in approved_kyc_vendor_ids
        b.title = b.quick_service.title if b.quick_service else b.package_name
        b.category_name = b.quick_service.category.name if (b.quick_service and b.quick_service.category) else 'Quick Service'
        b.budget = b.total_amount
        b.id_str = f"BK-{b.id:04d}"

    available_services = QuickService.objects.filter(status='active').select_related('vendor', 'vendor__vendor_profile', 'category', 'location').order_by('-created_at')[:8]
    total_available_services = QuickService.objects.filter(status='active').count()

    recent_jobs = job_list.select_related('category', 'location').order_by('-created_at')[:5]
    for j in recent_jobs:
        sel_vendor = j.assigned_vendor
        if not sel_vendor:
            sel_bid = j.bids.filter(status='selected').select_related('vendor', 'vendor__vendor_profile').first()
            if sel_bid:
                sel_vendor = sel_bid.vendor
        if sel_vendor:
            j.selected_vendor_name = sel_vendor.vendor_profile.company_name if hasattr(sel_vendor, 'vendor_profile') and sel_vendor.vendor_profile.company_name else (sel_vendor.get_full_name() or sel_vendor.username)
            j.is_vendor_verified = sel_vendor.id in approved_kyc_vendor_ids
        else:
            j.selected_vendor_name = None
            j.is_vendor_verified = False

    activity_items = []
    bids = Bid.objects.filter(job__user=user).select_related('vendor', 'vendor__vendor_profile', 'job').order_by('-created_at')[:5]
    for b in bids:
        vname = b.vendor.vendor_profile.company_name if hasattr(b.vendor, 'vendor_profile') and b.vendor.vendor_profile.company_name else (b.vendor.get_full_name() or b.vendor.username)
        target = b.job.title if b.job else 'Job'
        if b.status == 'selected':
            activity_items.append({
                'title': 'Vendor selected',
                'description': f"{vname} was selected for {target}.",
                'time': b.created_at.strftime('%d %b, %I:%M %p')
            })
        else:
            activity_items.append({
                'title': 'New quotation received',
                'description': f"{vname} quoted ₹{b.amount:,.0f} for {target}.",
                'time': b.created_at.strftime('%d %b, %I:%M %p')
            })

    return {
        'user_name': name,
        'user_initials': initials,
        'current_date': date_str,
        'user_location': user_location_str,
        'user_city': user_city,
        'user_state': user_state,
        'is_service_available': is_service_available,
        'service_not_available': not is_service_available,
        'service_unavailable_city': user_city,
        'active_qs': total_available_services,
        'user_active_bookings': active_qs,
        'available_services': available_services,
        'active_jobs': active_jobs,
        'pending_quotations': pending_quotations,
        'selected_vendors': selected_vendors,
        'completed_qs': completed_qs,
        'completed_jobs': completed_jobs,
        'recent_qs': recent_qs,
        'recent_jobs': recent_jobs,
        'recent_activity': activity_items,
    }

CITY_COORDINATES_MAP = {
    'mumbai': (19.0760, 72.8777),
    'bombay': (19.0760, 72.8777),
    'ranchi': (23.3697, 85.3346),
    'bengaluru': (12.9716, 77.5946),
    'bangalore': (12.9716, 77.5946),
    'delhi': (28.6139, 77.2090),
    'new delhi': (28.6139, 77.2090),
    'noida': (28.5355, 77.3910),
    'pune': (18.5204, 73.8567),
    'kolkata': (22.5726, 88.3639),
    'chennai': (13.0827, 80.2707),
    'hyderabad': (17.3850, 78.4867),
    'ahmedabad': (23.0225, 72.5714),
    'jaipur': (26.9124, 75.7873),
    'lucknow': (26.8467, 80.9462),
    'nagpur': (21.1458, 79.0882),
    'nashik': (19.9975, 73.7898),
    'indore': (22.7196, 75.8577),
    'chandigarh': (30.7333, 76.7794),
    'coimbatore': (11.0168, 76.9558),
    'mysuru': (12.2958, 76.6394),
    'jamshedpur': (22.8046, 86.2029),
    'dhanbad': (23.7957, 86.4304),
    'harmu': (23.3550, 85.3050),
    'morabadi': (23.3850, 85.3250),
    'doranda': (23.3340, 85.3218),
    'lalpur': (23.3697, 85.3346),
    'bariatu': (23.3950, 85.3500),
    'bandra': (19.0596, 72.8295),
    'andheri': (19.1136, 72.8697),
    'dadar': (19.0178, 72.8478),
}

def haversine_distance_km(lat1, lon1, lat2, lon2):
    """Calculates great-circle distance between two GPS coordinates in kilometers."""
    try:
        import math
        R = 6371.0 # Earth radius in km
        dlat = math.radians(float(lat2) - float(lat1))
        dlon = math.radians(float(lon2) - float(lon1))
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(float(lat1))) * math.cos(math.radians(float(lat2))) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(R * c, 1)
    except Exception:
        return None

def resolve_coordinates_for_location(loc_string, default_coords=(23.3697, 85.3346)):
    """Resolves coordinates from location string using CITY_COORDINATES_MAP."""
    if not loc_string:
        return default_coords
    s = loc_string.lower().strip()
    for key, coords in CITY_COORDINATES_MAP.items():
        if key in s:
            return coords
    return default_coords

def save_vendor_profile_changes(request, user):
    """
    Saves vendor profile details, contact information, and handles profile image upload/removal.
    Works seamlessly for both settings/index and profile/edit views.
    """
    v_prof, _ = VendorProfile.objects.get_or_create(user=user)
    u_prof, _ = UserProfile.objects.get_or_create(user=user)
    
    company_name = request.POST.get('company_name')
    if company_name is not None:
        v_prof.company_name = company_name.strip()

    vendor_type = request.POST.get('vendor_type')
    if vendor_type in ['vendor', 'company']:
        v_prof.vendor_type = vendor_type
    
    categories = request.POST.getlist('categories') or request.POST.getlist('category')
    if categories and any(c.strip() for c in categories):
        clean_cats = [c.strip() for c in categories if c.strip()]
        v_prof.category = ", ".join(clean_cats)
    else:
        category = request.POST.get('category')
        if category is not None and category.strip():
            v_prof.category = category.strip()
        
    location = request.POST.get('location')
    if location is not None and location.strip():
        v_prof.location = location.strip()
        
    address = request.POST.get('address')
    if address is not None:
        v_prof.address = address.strip()
        
    about = request.POST.get('about')
    if about is not None:
        v_prof.about = about.strip()
        
    experience = request.POST.get('experience')
    if experience is not None and str(experience).strip():
        try:
            v_prof.experience = int(experience)
        except (ValueError, TypeError):
            pass
            
    phone_number = request.POST.get('phone_number') or request.POST.get('mobile')
    if phone_number is not None and phone_number.strip():
        v_prof.mobile = phone_number.strip()
        u_prof.phone_number = phone_number.strip()
        u_prof.save()
        
    first_name = request.POST.get('first_name')
    if first_name is not None and first_name.strip():
        user.first_name = first_name.strip()
        
    email = request.POST.get('email')
    if email is not None and email.strip():
        user.email = email.strip()
        
    user.save()
    
    # Profile picture handling: Remove / Base64 / File upload
    remove_img = request.POST.get('remove_profile_image') in ['1', 'true', 'yes', True]
    if remove_img:
        if v_prof.profile_image:
            try:
                v_prof.profile_image.delete(save=False)
            except Exception:
                pass
            v_prof.profile_image = None
        if u_prof.profile_image:
            try:
                u_prof.profile_image.delete(save=False)
            except Exception:
                pass
            u_prof.profile_image = None
            u_prof.save()
    else:
        profile_image_base64 = request.POST.get('profile_image_base64', '').strip()
        if profile_image_base64 and ';base64,' in profile_image_base64:
            format_part, imgstr = profile_image_base64.split(';base64,', 1)
            ext = 'png' if 'png' in format_part else ('webp' if 'webp' in format_part else 'jpg')
            try:
                decoded = base64.b64decode(imgstr)
                fname = f"vendor_{user.id}_{uuid.uuid4().hex[:6]}.{ext}"
                v_prof.profile_image.save(fname, ContentFile(decoded), save=False)
            except Exception as err:
                print("Error saving cropped base64 image:", err)
        elif 'profile_image' in request.FILES and request.FILES['profile_image']:
            v_prof.profile_image = request.FILES['profile_image']
            
    v_prof.save()
    return v_prof, u_prof

def dashboard_view(request, path=''):
    from .models import VendorKYC, Category, VendorProfile, UserProfile
    if not path:
        path = 'index'
        
    if path.endswith('.html'):
        path = path[:-5]

    # Enforce authentication for user/ pages before proceeding
    if path.startswith('user/') and not request.user.is_authenticated:
        return redirect('register_user')

    # Enforce authentication for vendor/ pages before proceeding
    if path.startswith('vendor/') and not request.user.is_authenticated:
        return redirect(f'/login/?next=/{path}.html')

    # Subscriptions and Notifications modules completely removed
    if any(path.startswith(prefix) for prefix in ['subscriptions', 'admin-dashboard/subscriptions']) or path == 'subscriptions':
        messages.warning(request, "Access Denied: The subscriptions page has been removed.")
        return redirect('/admin-dashboard')

    if any(path.startswith(prefix) for prefix in ['notifications', 'admin-dashboard/notifications']) or path == 'notifications':
        messages.warning(request, "Access Denied: The notifications page has been removed.")
        return redirect('/admin-dashboard')

    if request.method == 'POST' and request.POST.get('action') in ['complete_and_settle', 'submit_completion_proof']:
        from .wallet_services import settle_job_completion
        job_id = request.POST.get('job_id')
        qs_id = request.POST.get('quick_service_id')
        work_summary = request.POST.get('work_summary', '').strip() or "Work completed in accordance with agreed service terms."
        photo_1 = request.FILES.get('photo_1')
        photo_2 = request.FILES.get('photo_2')

        if job_id:
            try:
                j_obj = Job.objects.get(id=job_id)
                has_selected_bid = Bid.objects.filter(job=j_obj, vendor=request.user, status__in=['selected', 'completed']).exists()
                if request.user.is_authenticated and (request.user == j_obj.user or request.user.role == 'ADMIN' or request.user == j_obj.assigned_vendor or has_selected_bid):
                    settle_job_completion(job=j_obj)
                    j_obj.status = 'completed'
                    if not j_obj.assigned_vendor and has_selected_bid:
                        j_obj.assigned_vendor = request.user
                    j_obj.save()
                    Bid.objects.filter(job=j_obj, status='selected').update(status='completed')
                    # Save work completion proof
                    proof_vendor = j_obj.assigned_vendor or (request.user if request.user.role == 'VENDOR' else None)
                    if not proof_vendor:
                        sel_bid = Bid.objects.filter(job=j_obj, status='completed').first()
                        if sel_bid:
                            proof_vendor = sel_bid.vendor
                    if photo_1 or work_summary:
                        JobCompletionProof.objects.update_or_create(
                            job=j_obj,
                            defaults={
                                'vendor': proof_vendor or request.user,
                                'work_summary': work_summary,
                                **({'photo_1': photo_1} if photo_1 else {}),
                                **({'photo_2': photo_2} if photo_2 else {}),
                            }
                        )
            except Job.DoesNotExist:
                pass
        elif qs_id:
            try:
                qs_obj = QuickService.objects.get(id=qs_id)
                has_selected_bid = Bid.objects.filter(quick_service=qs_obj, vendor=request.user, status__in=['selected', 'completed']).exists()
                if request.user.is_authenticated and (request.user == qs_obj.user or request.user.role == 'ADMIN' or has_selected_bid):
                    settle_job_completion(quick_service=qs_obj)
                    qs_obj.status = 'completed'
                    qs_obj.save()
                    Bid.objects.filter(quick_service=qs_obj, status='selected').update(status='completed')
                    sel_bid = Bid.objects.filter(quick_service=qs_obj, status__in=['selected', 'completed']).first()
                    proof_vendor = (request.user if request.user.role == 'VENDOR' else (sel_bid.vendor if sel_bid else None))
                    if (photo_1 or work_summary) and proof_vendor:
                        JobCompletionProof.objects.update_or_create(
                            quick_service=qs_obj,
                            defaults={
                                'vendor': proof_vendor,
                                'work_summary': work_summary,
                                **({'photo_1': photo_1} if photo_1 else {}),
                                **({'photo_2': photo_2} if photo_2 else {}),
                            }
                        )
            except QuickService.DoesNotExist:
                pass
        referer = request.META.get('HTTP_REFERER')
        return redirect(referer if referer else '/vendor/jobs/selected-jobs.html')

    if request.method == 'POST' and (request.POST.get('action') == 'submit_review' or path == 'user/reviews/create'):
        if request.user.is_authenticated:
            try:
                rating_val = int(request.POST.get('rating', 5))
            except (ValueError, TypeError):
                rating_val = 5
            review_title = request.POST.get('review_title', '').strip()
            comment = request.POST.get('comment', '').strip() or request.POST.get('review', '').strip()
            review_image = request.FILES.get('review_image') or request.FILES.get('review_images')
            job_id = request.POST.get('job_id')
            qs_id = request.POST.get('quick_service_id')
            vendor_id = request.POST.get('vendor_id')
            booking_key = request.POST.get('booking_id') or request.POST.get('related_booking') or request.POST.get('related_item')

            target_booking_id = None
            if booking_key:
                _bk = str(booking_key)
                if _bk.startswith('job:'):
                    job_id = _bk.split(':')[1]
                elif _bk.startswith('booking:') or _bk.startswith('qs:'):
                    target_booking_id = _bk.split(':')[1]
                elif _bk.isdigit():
                    target_booking_id = _bk
            # Legacy links pass the booking id as quick_service_id
            if not target_booking_id and qs_id and not job_id:
                target_booking_id = qs_id

            if target_booking_id:
                try:
                    _review, _created = submit_booking_review(
                        customer=request.user,
                        booking_id=target_booking_id,
                        rating=rating_val,
                        comment=comment,
                        title=review_title,
                        image=review_image,
                    )
                    messages.success(request, 'Thank you! Your review has been submitted.' if _created else 'Your review has been updated.')
                except ReviewError as e:
                    messages.error(request, e.message)
                return redirect('/user/reviews/index.html')

            target_job = Job.objects.filter(id=job_id).first() if job_id else None
            target_qs = QuickService.objects.filter(id=qs_id).first() if qs_id else None
            target_vendor = None

            if vendor_id:
                target_vendor = User.objects.filter(id=vendor_id).first()
            if not target_vendor and target_job:
                if target_job.assigned_vendor:
                    target_vendor = target_job.assigned_vendor
                else:
                    sel_bid = Bid.objects.filter(job=target_job, status__in=['selected', 'completed']).first()
                    if sel_bid:
                        target_vendor = sel_bid.vendor
            if not target_vendor and target_qs:
                sel_bid = Bid.objects.filter(quick_service=target_qs, status__in=['selected', 'completed']).first()
                if sel_bid:
                    target_vendor = sel_bid.vendor

            if target_vendor and comment:
                ServiceReview.objects.update_or_create(
                    customer=request.user,
                    job=target_job,
                    quick_service=target_qs,
                    vendor=target_vendor,
                    defaults={
                        'rating': min(max(rating_val, 1), 5),
                        'review_title': review_title,
                        'comment': comment,
                        **({'review_image': review_image} if review_image else {}),
                        'status': 'published'
                    }
                )
            referer = request.META.get('HTTP_REFERER')
            return redirect('/user/reviews/index.html')

    if request.method == 'POST' and request.POST.get('action') == 'accept_vendor':
        bid_id = request.POST.get('bid_id')
        if bid_id:
            try:
                b_obj = Bid.objects.get(id=bid_id)
                b_obj.status = 'selected'
                b_obj.save()
                if b_obj.quick_service:
                    b_obj.quick_service.status = 'selected'
                    b_obj.quick_service.save()
                if b_obj.job:
                    b_obj.job.assigned_vendor = b_obj.vendor
                    b_obj.job.status = 'selected'
                    b_obj.job.save()
            except Bid.DoesNotExist:
                pass
        referer = request.META.get('HTTP_REFERER')
        return redirect(referer if referer else '/user/dashboard')

    if path in ['accounts/login', 'accounts/login/', 'login', 'login/']:
        return user_login_view(request)

    if path in ['dashboard', 'admin-dashboard', 'admin-dashboard/dashboard', 'admin-dashboard/index']:
        return admin_dashboard(request)

    if path in ['vendor/dashboard', 'vendor/index', 'vendor', 'infinity-vendor-dashboard/dashboard', 'infinity-vendor-dashboard/index', 'infinity-vendor-dashboard']:
        return vendor_dashboard(request)

    if path in ['user/dashboard', 'user/index', 'user', 'user-dashboard/dashboard', 'user-dashboard/index', 'user-dashboard']:
        return user_dashboard(request)
        
    # Deprecated user/quick-services/create endpoint removed

    if request.method == 'POST' and request.POST.get('action') == 'toggle_job_status':
        job_id = request.POST.get('job_id')
        if job_id:
            try:
                job = Job.objects.get(id=job_id, user=request.user)
                if job.status == 'open':
                    job.status = 'closed'
                elif job.status == 'closed':
                    job.status = 'open'
                job.save()
            except Job.DoesNotExist:
                pass
        return redirect('/user/jobs/index.html')

    if request.method == 'POST' and path in ['user/jobs/create', 'jobs/create']:
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        cat_id = request.POST.get('category') or request.POST.get('category_id')
        budget = request.POST.get('budget', 500)
        locality = request.POST.get('locality', '').strip() or "Ranchi Central"
        address = request.POST.get('address', '').strip() or locality
        pincode = request.POST.get('pincode', '834001')
        contact_name = request.POST.get('contact_name') or (request.user.get_full_name() or request.user.username)
        contact_mobile = request.POST.get('contact_mobile', '')
        pref_date = request.POST.get('preferred_start_date') or None
        
        lat_val = request.POST.get('latitude')
        lon_val = request.POST.get('longitude')
        lat = None
        lon = None
        if lat_val:
            try: lat = float(lat_val)
            except (ValueError, TypeError): pass
        if lon_val:
            try: lon = float(lon_val)
            except (ValueError, TypeError): pass

        job = Job(
            title=title or "Home Service Job",
            description=description or f"Requirement for {title}",
            required_work=request.POST.getlist('required_work[]') or [title or "Work"],
            scope_of_work=request.POST.get('scope_of_work', ''),
            materials_details=request.POST.get('materials_details', ''),
            additional_requirements=request.POST.get('additional_requirements', ''),
            budget=budget if budget else 500,
            budget_type=request.POST.get('budget_type', 'Fixed Price'),
            preferred_start_date=pref_date,
            expected_completion=request.POST.get('expected_completion') or None,
            required_time=request.POST.get('required_time', 'Flexible'),
            shift_availability=request.POST.get('shift_availability', 'Day shift'),
            working_hours=request.POST.get('working_hours', 'Regular'),
            locality=locality,
            latitude=lat,
            longitude=lon,
            address=address,
            pincode=pincode,
            contact_name=contact_name,
            contact_mobile=contact_mobile,
            user=request.user,
            status='open'
        )
        if cat_id:
            try: job.category_id = int(cat_id)
            except: pass
        
        loc_id = request.POST.get('location_id')
        if loc_id:
            try: job.location_id = int(loc_id)
            except: pass
        if not job.location_id:
            first_loc = Location.objects.filter(status='active').first()
            if first_loc: job.location = first_loc

        uploaded_files = request.FILES.getlist('images') or request.FILES.getlist('image')
        if uploaded_files:
            job.image = uploaded_files[0]
            job.save()
            for img_file in uploaded_files:
                JobImage.objects.create(job=job, image=img_file)
        else:
            job.save()

        return redirect('/user/jobs/index.html')

    if request.method == 'POST' and (path in ['vendor/catalog/index', 'vendor/catalog', 'infinity-vendor-dashboard/catalog/index'] or 'catalog' in path):
        if request.user.is_authenticated:
            action = request.POST.get('action')
            if action == 'delete_service':
                srv_id = request.POST.get('service_id')
                if srv_id:
                    QuickService.objects.filter(id=srv_id, vendor=request.user).delete()
                    messages.success(request, "Service removed from catalog successfully.")
                return redirect('/vendor/catalog/index.html')

            if action == 'toggle_status':
                srv_id = request.POST.get('service_id')
                new_status = request.POST.get('status', '').strip().lower()
                if new_status in ['active', 'paused', 'draft'] and srv_id:
                    qs_obj = QuickService.objects.filter(id=srv_id, vendor=request.user).first()
                    if qs_obj:
                        qs_obj.status = new_status
                        qs_obj.save(update_fields=['status'])
                        messages.success(request, f"Service '{qs_obj.title}' status updated to {qs_obj.get_status_display()}.")
                return redirect('/vendor/catalog/index.html')

            if action == 'edit_service':
                srv_id = request.POST.get('service_id')
                qs_obj = QuickService.objects.filter(id=srv_id, vendor=request.user).first()
                if not qs_obj:
                    messages.error(request, "Service not found or unauthorized.")
                    return redirect('/vendor/catalog/index.html')

                title = request.POST.get('title', '').strip() or qs_obj.title
                category_id = request.POST.get('category_id')
                new_status = request.POST.get('status', qs_obj.status).strip().lower()
                if new_status not in ['active', 'paused', 'draft']:
                    new_status = qs_obj.status
                description = request.POST.get('description', '').strip()
                locality = request.POST.get('locality', '').strip() or qs_obj.locality
                radius_val = request.POST.get('service_radius_km')
                lat_val = request.POST.get('latitude')
                lon_val = request.POST.get('longitude')

                if category_id:
                    cat_obj = Category.objects.filter(id=category_id).first()
                    if cat_obj:
                        qs_obj.category = cat_obj

                if radius_val:
                    try: qs_obj.service_radius_km = float(radius_val)
                    except (ValueError, TypeError): pass

                if lat_val:
                    try: qs_obj.latitude = float(lat_val)
                    except (ValueError, TypeError): pass

                if lon_val:
                    try: qs_obj.longitude = float(lon_val)
                    except (ValueError, TypeError): pass

                # Global settings for Single-Price backend markup calculation
                gs = GlobalSettings.objects.first()

                # Parse packages
                service_packages = []
                packages_json = request.POST.get('packages_json')
                if packages_json:
                    try:
                        parsed_pkgs = json.loads(packages_json)
                        if isinstance(parsed_pkgs, list):
                            for p in parsed_pkgs:
                                if isinstance(p, dict) and p.get('name'):
                                    p_raw = float(p.get('vendor_payout', p.get('price', 199.0)))
                                    calc = gs.calculate_qs_customer_price(p_raw) if gs else {'customer_price': round(p_raw), 'vendor_payout': p_raw, 'commission': 0, 'total_tax': 0}
                                    service_packages.append({
                                        'name': str(p.get('name')).strip(),
                                        'price': calc['customer_price'],
                                        'vendor_payout': calc['vendor_payout'],
                                        'commission': calc.get('commission', 0),
                                        'tax': calc.get('total_tax', 0),
                                        'desc': str(p.get('desc', '')).strip()
                                    })
                    except Exception:
                        pass

                if not service_packages:
                    pkg_names = request.POST.getlist('package_name[]')
                    pkg_prices = request.POST.getlist('package_price[]')
                    pkg_descs = request.POST.getlist('package_desc[]')
                    for i, name in enumerate(pkg_names):
                        if not name.strip():
                            continue
                        try: p_val = float(pkg_prices[i]) if i < len(pkg_prices) else 199.0
                        except (ValueError, TypeError): p_val = 199.0
                        calc = gs.calculate_qs_customer_price(p_val) if gs else {'customer_price': round(p_val), 'vendor_payout': p_val, 'commission': 0, 'total_tax': 0}
                        d_val = pkg_descs[i].strip() if i < len(pkg_descs) else ""
                        service_packages.append({
                            'name': name.strip(),
                            'price': calc['customer_price'],
                            'vendor_payout': calc['vendor_payout'],
                            'commission': calc.get('commission', 0),
                            'tax': calc.get('total_tax', 0),
                            'desc': d_val
                        })

                if service_packages:
                    qs_obj.service_packages = service_packages
                    qs_obj.base_price = min(p['price'] for p in service_packages)

                # Parse Inclusions
                inclusions = []
                inclusions_json = request.POST.get('inclusions_json')
                if inclusions_json:
                    try:
                        p_inc = json.loads(inclusions_json)
                        if isinstance(p_inc, list):
                            inclusions = [str(x).strip() for x in p_inc if str(x).strip()]
                    except Exception: pass
                if not inclusions:
                    inclusions = [str(x).strip() for x in request.POST.getlist('inclusions[]') if str(x).strip()]
                if inclusions:
                    qs_obj.inclusions = inclusions

                # Parse Exclusions
                exclusions = []
                exclusions_json = request.POST.get('exclusions_json')
                if exclusions_json:
                    try:
                        p_exc = json.loads(exclusions_json)
                        if isinstance(p_exc, list):
                            exclusions = [str(x).strip() for x in p_exc if str(x).strip()]
                    except Exception: pass
                if not exclusions:
                    exclusions = [str(x).strip() for x in request.POST.getlist('exclusions[]') if str(x).strip()]
                if exclusions:
                    qs_obj.exclusions = exclusions

                # Image Handling
                image_file = request.FILES.get('image')
                if image_file:
                    qs_obj.image = image_file
                image_preset = request.POST.get('image_preset', '').strip()
                if image_preset:
                    qs_obj.image_url = image_preset

                qs_obj.title = title
                qs_obj.status = new_status
                qs_obj.description = description
                qs_obj.locality = locality
                qs_obj.save()

                messages.success(request, f"Service '{title}' updated successfully!")
                return redirect('/vendor/catalog/index.html')

            title = request.POST.get('title', '').strip() or "Quick Home Service"
            category_id = request.POST.get('category_id')
            base_price = request.POST.get('base_price', '199')
            description = request.POST.get('description', '').strip()

            vp = getattr(request.user, 'vendor_profile', None)
            default_locality = ""
            if vp and vp.location:
                default_locality = vp.location.strip()
            elif getattr(request.user, 'assigned_city', None):
                default_locality = request.user.assigned_city.strip()
            if not default_locality:
                default_locality = "Lalpur, Ranchi"

            locality = request.POST.get('locality', '').strip() or default_locality
            lat_val = request.POST.get('latitude')
            lon_val = request.POST.get('longitude')
            radius_val = request.POST.get('service_radius_km', 10.0)

            default_lat = 23.3697
            default_lon = 85.3346
            for city_key, coords in CITY_COORDINATES_MAP.items():
                if city_key in locality.lower():
                    default_lat, default_lon = coords
                    break

            try: lat = float(lat_val) if lat_val else default_lat
            except (ValueError, TypeError): lat = default_lat

            try: lon = float(lon_val) if lon_val else default_lon
            except (ValueError, TypeError): lon = default_lon

            try: radius = float(radius_val) if radius_val else 10.0
            except (ValueError, TypeError): radius = 10.0

            try: default_price = float(base_price) if base_price else 199.0
            except (ValueError, TypeError): default_price = 199.0

            cat_obj = Category.objects.filter(id=category_id).first() if category_id else Category.objects.filter(status='active').first()

            # Fetch financial settings for backend Quick Service price calculation
            gs = GlobalSettings.objects.first()

            # Parse Package Options
            service_packages = []
            packages_json = request.POST.get('packages_json')
            if packages_json:
                try:
                    parsed_pkgs = json.loads(packages_json)
                    if isinstance(parsed_pkgs, list):
                        for p in parsed_pkgs:
                            if isinstance(p, dict) and p.get('name'):
                                p_raw = float(p.get('price', default_price))
                                calc = gs.calculate_qs_customer_price(p_raw) if gs else {'customer_price': round(p_raw), 'vendor_payout': p_raw, 'commission': 0, 'total_tax': 0}
                                service_packages.append({
                                    'name': str(p.get('name')).strip(),
                                    'price': calc['customer_price'],        # Customer listed price (Base + Cut + GST)
                                    'vendor_payout': calc['vendor_payout'],  # Vendor payout
                                    'commission': calc.get('commission', 0),
                                    'tax': calc.get('total_tax', 0),
                                    'desc': str(p.get('desc', '')).strip()
                                })
                except Exception:
                    pass

            if not service_packages:
                pkg_names = request.POST.getlist('package_name[]')
                pkg_prices = request.POST.getlist('package_price[]') # Vendor base payout price
                pkg_descs = request.POST.getlist('package_desc[]')

                for i, name in enumerate(pkg_names):
                    if not name.strip():
                        continue
                    try: p_val = float(pkg_prices[i]) if i < len(pkg_prices) else default_price
                    except (ValueError, TypeError): p_val = default_price

                    calc = gs.calculate_qs_customer_price(p_val) if gs else {'customer_price': round(p_val), 'vendor_payout': p_val, 'commission': 0, 'total_tax': 0}
                    d_val = pkg_descs[i].strip() if i < len(pkg_descs) else ""
                    service_packages.append({
                        'name': name.strip(),
                        'price': calc['customer_price'],        # Customer listed price
                        'vendor_payout': calc['vendor_payout'],  # Vendor payout
                        'commission': calc.get('commission', 0),
                        'tax': calc.get('total_tax', 0),
                        'desc': d_val
                    })

            if not service_packages:
                calc = gs.calculate_qs_customer_price(default_price) if gs else {'customer_price': round(default_price), 'vendor_payout': default_price, 'commission': 0, 'total_tax': 0}
                service_packages = [
                    {
                        'name': 'Standard Service',
                        'price': calc['customer_price'],
                        'vendor_payout': calc['vendor_payout'],
                        'commission': calc.get('commission', 0),
                        'tax': calc.get('total_tax', 0),
                        'desc': description or f"Full {title} service by verified professional."
                    }
                ]

            # Lowest customer package price sets the starting listed price
            min_price = min(p['price'] for p in service_packages)

            # Parse Inclusions
            inclusions = []
            inclusions_json = request.POST.get('inclusions_json')
            if inclusions_json:
                try:
                    parsed_inc = json.loads(inclusions_json)
                    if isinstance(parsed_inc, list):
                        inclusions = [str(x).strip() for x in parsed_inc if str(x).strip()]
                except Exception:
                    pass

            if not inclusions:
                inclusions = [str(x).strip() for x in request.POST.getlist('inclusions[]') if str(x).strip()]

            if not inclusions:
                inclusions = [
                    "Complete diagnostic inspection of existing fittings & components",
                    "Execution by certified, background-checked professional",
                    "Post-service sanitization and thorough debris cleanup",
                    "30 days Sugu protection warranty on all workmanship"
                ]

            # Parse Exclusions
            exclusions = [str(x).strip() for x in request.POST.getlist('exclusions[]') if str(x).strip()]
            if not exclusions:
                exclusions = [
                    "Major civil masonry, pipe embedding or wall tearing excluded",
                    "Spare parts / extra hardware to be purchased or charged separately"
                ]

            # Handle Image Upload or Preset
            image_file = request.FILES.get('image')
            image_preset = request.POST.get('image_preset', '').strip()

            qs_obj = QuickService(
                vendor=request.user,
                title=title,
                category=cat_obj,
                description=description or f"Quality {title} service at your doorstep.",
                base_price=min_price,
                service_packages=service_packages,
                inclusions=inclusions,
                exclusions=exclusions,
                image_url=image_preset or None,
                locality=locality,
                latitude=lat,
                longitude=lon,
                service_radius_km=radius,
                status=request.POST.get('status', 'active').strip().lower() if request.POST.get('status', 'active').strip().lower() in ['active', 'paused', 'draft'] else 'active'
            )
            if image_file:
                qs_obj.image = image_file
            qs_obj.save()

            messages.success(request, f"Service '{title}' published successfully with {len(service_packages)} package tier(s)!")
            return redirect('/vendor/catalog/index.html')

    # Redirect bare vendor routes to canonical /vendor/ routes
    if path in ['catalog', 'catalog/index', 'catalog/index.html'] or path.startswith('catalog/'):
        clean_sub = path if path.endswith('.html') else f"{path}.html"
        return redirect(f'/vendor/{clean_sub}')

    if path in ['bookings', 'bookings/index', 'bookings/index.html'] or path.startswith('bookings/'):
        clean_sub = path if path.endswith('.html') else f"{path}.html"
        return redirect(f'/vendor/{clean_sub}')

    if path.startswith('bid-credits/'):
        clean_sub = path if path.endswith('.html') else f"{path}.html"
        return redirect(f'/vendor/{clean_sub}')

    # Map url prefixes to correct template directories
    mapped_path = path
    admin_subfolders = ['users/', 'quick-services/', 'jobs/', 'bidding/', 'payments/', 'reviews/', 'complaints/', 'reports/', 'master/']
    if any(mapped_path.startswith(folder) for folder in admin_subfolders):
        mapped_path = f'admin-dashboard/{mapped_path}'
    elif mapped_path.startswith('user/'):
        mapped_path = mapped_path.replace('user/', 'user-dashboard/', 1)
    elif mapped_path.startswith('vendor/'):
        mapped_path = mapped_path.replace('vendor/', 'infinity-vendor-dashboard/', 1)

    ext = os.path.splitext(mapped_path)[1]
    if ext and ext not in ['.html']:
        file_path = settings.BASE_DIR / 'templates' / mapped_path
        if file_path.exists():
            content_type, _ = mimetypes.guess_type(str(file_path))
            with open(file_path, 'rb') as f:
                return HttpResponse(f.read(), content_type=content_type or 'application/octet-stream')
        else:
            raise Http404(f"Asset {path} not found")
        
    template_name = f'{mapped_path}.html'
    context = {}
    
    if path.startswith('vendor/'):
        context['vendor_name'] = "Vendor"
        context['vendor_initials'] = "VN"
        context['vendor_location'] = "Ranchi"
        context['vendor_city'] = "Ranchi"
        context['vendor_type'] = "Individual Vendor"
        context['wallet_balance'] = "0.00"
        context['available_bids'] = 5
        context['remaining_credits'] = 5
        try:
            context['all_categories'] = Category.objects.filter(status='active').order_by('name')
        except Exception:
            pass

        if request.user.is_authenticated:
            try:
                from .wallet_services import get_or_create_wallet
                wallet = get_or_create_wallet(request.user)
                context['wallet_balance'] = f"{wallet.available_balance:.2f}"
                context['vendor_wallet'] = wallet
                
                vendor_profile = getattr(request.user, 'vendor_profile', None)
                if not vendor_profile and request.user.role == 'VENDOR':
                    vendor_profile, _ = VendorProfile.objects.get_or_create(user=request.user)
                user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
                
                context['vendor_profile'] = vendor_profile
                context['user_profile'] = user_profile
                
                kyc_doc = VendorKYC.objects.filter(vendor=request.user).first()
                context['kyc'] = kyc_doc
                context['is_kyc_verified'] = (kyc_doc.status == 'approved') if kyc_doc else False
                context['all_categories'] = Category.objects.filter(status='active').order_by('name')

                # Determine display vendor name & vendor classification
                display_name = None
                if vendor_profile:
                    if vendor_profile.vendor_type == 'company' and vendor_profile.company_name and vendor_profile.company_name.strip():
                        display_name = vendor_profile.company_name.strip()
                    elif vendor_profile.company_name and vendor_profile.company_name.strip() and vendor_profile.company_name.strip().lower() != request.user.first_name.strip().lower():
                        display_name = vendor_profile.company_name.strip()

                if not display_name:
                    display_name = request.user.get_full_name() or request.user.first_name or request.user.username
                    
                context['vendor_name'] = display_name
                context['vendor_initials'] = display_name[:2].upper() if display_name else "VN"
                loc = (vendor_profile.location if (vendor_profile and vendor_profile.location) else "Ranchi")
                context['vendor_location'] = loc
                context['vendor_city'] = loc.split(',')[0].strip() if loc else "Ranchi"
                
                if vendor_profile and vendor_profile.vendor_type == 'company':
                    context['vendor_type'] = "Company Vendor"
                else:
                    context['vendor_type'] = "Individual Vendor"
                
                prof_img = None
                if vendor_profile and vendor_profile.profile_image:
                    try:
                        prof_img = vendor_profile.profile_image.url
                    except Exception:
                        prof_img = None
                if not prof_img and user_profile and user_profile.profile_image:
                    try:
                        prof_img = user_profile.profile_image.url
                    except Exception:
                        prof_img = None
                context['profile_image_url'] = prof_img
                context['remaining_credits'] = getattr(vendor_profile, 'available_bids', 5) if vendor_profile else 5
                context['available_bids'] = getattr(vendor_profile, 'available_bids', 5) if vendor_profile else 5
            except Exception as e:
                print("Error initializing vendor context:", e)
            
    # Inject dynamic user data
    if 'master/categories' in path:
        if request.user.is_authenticated and request.user.role == 'ADMIN' and not request.user.is_superuser:
            messages.error(request, "Permission Denied: Category management is restricted to Super Admin.")
            return redirect('/admin-dashboard')
        categories = Category.objects.all().order_by('-created_at')
        categories_data = []
        for cat in categories:
            categories_data.append({
                'id': cat.id,
                'name': cat.name,
                'service_type': cat.service_type,
                'status': cat.status,
                'created_at': cat.created_at.strftime('%Y-%m-%d') if cat.created_at else 'Unknown'
            })
        context['categories_json'] = json.dumps(categories_data)
        
    if 'jobs/create' in path or 'quick-services/create' in path:
        active_cats = Category.objects.filter(status='active').order_by('name')
        context['categories'] = active_cats
        cat_data = [{'id': c.id, 'name': c.name, 'service_type': c.service_type} for c in active_cats]
        context['categories_json'] = json.dumps(cat_data)
        active_locs = Location.objects.filter(status='active').order_by('state', 'city')
        context['locations'] = active_locs
        loc_data = [{'id': l.id, 'state': l.state, 'city': l.city, 'status': l.status} for l in active_locs]
        context['locations_json'] = json.dumps(loc_data)

    if 'catalog' in path:
        context['categories'] = Category.objects.filter(status='active').order_by('name')
        if request.user.is_authenticated:
            context['my_services'] = QuickService.objects.filter(vendor=request.user).select_related('category').order_by('-created_at')
        # Pass financial settings for dynamic pricing in live preview
        gs = GlobalSettings.objects.first()
        if gs:
            context['platform_commission_percent'] = gs.get_qs_commission_percent()
            context['cgst_percent'] = gs.get_qs_cgst_percent()
            context['sgst_percent'] = gs.get_qs_sgst_percent()
            context['platform_flat_fee'] = gs.get_qs_flat_fee()
            context['tax_calculation_mode'] = gs.get_qs_tax_mode()
        else:
            context['platform_commission_percent'] = 10.0
            context['cgst_percent'] = 9.0
            context['sgst_percent'] = 9.0
            context['platform_flat_fee'] = 0.0
            context['tax_calculation_mode'] = 'commission_only'

    if path in ['user/quick-services/index', 'user/quick-services', 'user/quick-services/create', 'user/quick-services/details']:
        return redirect('/user/services/browse.html')

    if path in ['user/quick-services/details', 'quick-services/details'] and path.startswith('user/'):
        qs_id = request.GET.get('id')
        if qs_id:
            try:
                qs = ServiceBooking.objects.select_related("quick_service", "vendor").get(id=qs_id, customer=request.user)
                context['qs'] = qs
                
                bids = Bid.objects.filter(quick_service_id=qs_id).select_related('vendor', 'vendor__vendor_profile')
                context['bids'] = bids
                bids_data = []
                for bid in bids:
                    vendor = bid.vendor
                    try:
                        profile = vendor.vendor_profile
                    except:
                        profile = None
                        
                    vendor_name = vendor.get_full_name() or vendor.username
                    if profile and profile.company_name:
                        vendor_name = profile.company_name
                        
                    bids_data.append({
                        'bid': bid,
                        'id': bid.id,
                        'vendor_name': vendor_name,
                        'vendor_initials': vendor_name[:2].upper(),
                        'vendor_type': 'Service Company' if (profile and profile.company_name) else 'Independent Technician',
                        'rating': float(profile.rating) if (profile and profile.rating) else 4.8,
                        'experience': profile.experience if profile and profile.experience else 5,
                        'completed_jobs': Job.objects.filter(bids__vendor=vendor, status='completed').distinct().count() or 12,
                        'proposal': bid.proposal or 'Inspection and repair included.',
                        'estimated_time': bid.estimated_time or '2-3 hours',
                        'amount': float(bid.amount),
                        'status': bid.status
                    })
                context['bids_data'] = bids_data
                
                selected_bid_data = next((b for b in bids_data if b['bid'].status == 'selected'), None)
                context['selected_bid_data'] = selected_bid_data
                
                if qs.preferred_date and qs.preferred_time:
                    context['preferred_datetime'] = f"{qs.preferred_date.strftime('%d %b %Y')} · {qs.preferred_time.strftime('%I:%M %p')}"
                elif qs.preferred_date:
                    context['preferred_datetime'] = qs.preferred_date.strftime('%d %b %Y')
                else:
                    context['preferred_datetime'] = "Not specified"
                    
                context['completion_proof'] = getattr(qs, 'completion_proof', None)
                if request.user.is_authenticated:
                    context['user_review'] = ServiceReview.objects.filter(quick_service=qs, customer=request.user).first()
                    
            except QuickService.DoesNotExist:
                return redirect('/user/quick-services/index.html')
        else:
            return redirect('/user/quick-services/index.html')

    if path in ['user/quick-services/quotations', 'user/quick-services/compare']:
        qs_id = request.GET.get('id') or request.GET.get('qs_id')
        if qs_id:
            try:
                qs = ServiceBooking.objects.select_related("quick_service", "vendor").get(id=qs_id, customer=request.user)
                context['qs'] = qs
                bids = Bid.objects.filter(quick_service_id=qs_id).select_related('vendor', 'vendor__vendor_profile')
                context['bids'] = bids
            except QuickService.DoesNotExist:
                bids = []
            bids_data = []
            for bid in bids:
                vendor = bid.vendor
                try:
                    profile = vendor.vendor_profile
                except:
                    profile = None
                
                vendor_name = vendor.get_full_name() or vendor.username
                if profile and profile.company_name:
                    vendor_name = profile.company_name

                bids_data.append({
                    'id': bid.id,
                    'vendor_id': vendor.id,
                    'price': float(bid.amount),
                    'estimated_time': bid.estimated_time or '1-2 Days',
                    'vendor_name': vendor_name,
                    'vendor_initials': vendor_name[:2].upper(),
                    'vendor_category': profile.category if profile else 'General',
                    'rating': float(profile.rating) if profile and profile.rating else 4.8,
                    'experience': profile.experience if profile and profile.experience else 5,
                    'completed_jobs': 12,
                    'availability': 'available',
                    'status': bid.status
                })
            context['quotations_json'] = json.dumps(bids_data)
        else:
            context['quotations_json'] = '[]'

    if path in ['user/jobs/details', 'jobs/details'] and path.startswith('user/'):
        job_id = request.GET.get('id')
        if job_id:
            try:
                job = Job.objects.select_related('category', 'location').get(id=job_id, user=request.user)
                context['job'] = job
                
                bids = Bid.objects.filter(job_id=job_id).select_related('vendor', 'vendor__vendor_profile')
                context['bids'] = bids
                
                bids_count = bids.count()
                lowest_bid = None
                highest_bid = None
                selected_vendors_count = bids.filter(status='selected').count()
                
                if bids_count > 0:
                    lowest_bid = bids.order_by('amount').first()
                    highest_bid = bids.order_by('-amount').first()
                    
                context['job_stats'] = {
                    'total_bids': bids_count,
                    'lowest_amount': float(lowest_bid.amount) if lowest_bid else 0,
                    'lowest_vendor': (lowest_bid.vendor.vendor_profile.company_name if hasattr(lowest_bid.vendor, 'vendor_profile') and lowest_bid.vendor.vendor_profile.company_name else (lowest_bid.vendor.get_full_name() or lowest_bid.vendor.username)) if lowest_bid else '—',
                    'highest_amount': float(highest_bid.amount) if highest_bid else 0,
                    'highest_vendor': (highest_bid.vendor.vendor_profile.company_name if hasattr(highest_bid.vendor, 'vendor_profile') and highest_bid.vendor.vendor_profile.company_name else (highest_bid.vendor.get_full_name() or highest_bid.vendor.username)) if highest_bid else '—',
                    'selected_count': selected_vendors_count,
                }
                
                context['start_date_fmt'] = job.preferred_start_date.strftime('%d %B %Y') if job.preferred_start_date else "Not specified"
                context['end_date_fmt'] = job.expected_completion.strftime('%d %B %Y') if job.expected_completion else "Not specified"
                
                context['completion_proof'] = getattr(job, 'completion_proof', None)
                if request.user.is_authenticated:
                    context['user_review'] = ServiceReview.objects.filter(job=job, customer=request.user).first()
                    
            except Job.DoesNotExist:
                return redirect('/user/jobs/index.html')
        else:
            return redirect('/user/jobs/index.html')

    if path in ['user/jobs/index', 'user/jobs']:
        if request.user.is_authenticated:
            job_list = Job.objects.filter(user=request.user).select_related('category', 'location').order_by('-created_at')
            for j in job_list:
                sel = j.bids.filter(status='selected').select_related('vendor', 'vendor__vendor_profile').first()
                if sel:
                    j.selected_vendor_name = sel.vendor.vendor_profile.company_name if hasattr(sel.vendor, 'vendor_profile') and sel.vendor.vendor_profile.company_name else (sel.vendor.get_full_name() or sel.vendor.username)
                else:
                    j.selected_vendor_name = '—'
            context['jobs'] = job_list
            context['status_counts'] = {
                'all': job_list.count(),
                'open': job_list.filter(status='open').count(),
                'selected': job_list.filter(status='selected').count(),
                'progress': job_list.filter(status='progress').count(),
                'completed': job_list.filter(status='completed').count(),
                'cancelled': job_list.filter(status='cancelled').count(),
                'closed': job_list.filter(status='closed').count(),
            }
        else:
            context['jobs'] = []
            context['status_counts'] = {'all':0,'open':0,'selected':0,'progress':0,'completed':0,'cancelled':0,'closed':0}
            context['active_cats'] = []

    # ── USER SUPPORT & DISPUTE TICKETS ──
    if 'support/complaints' in path or 'support/create-complaint' in path or 'support/complaint-details' in path or path == 'user/support/index' or path == 'user/support':
        if not request.user.is_authenticated:
            return redirect('/login/?next=/' + path + '.html')

        if 'support/complaints' in path:
            status_filter = request.GET.get('status')
            q_filter = request.GET.get('q', '').strip()

            user_disputes = DisputeTicket.objects.filter(
                Q(raised_by=request.user) | Q(against_user=request.user)
            ).select_related('raised_by', 'against_user', 'job', 'quick_service').order_by('-created_at')

            all_user_disputes = DisputeTicket.objects.filter(
                Q(raised_by=request.user) | Q(against_user=request.user)
            )
            context['count_all'] = all_user_disputes.count()
            context['count_open'] = all_user_disputes.filter(status='open').count()
            context['count_review'] = all_user_disputes.filter(status='investigating').count()
            context['count_resolved'] = all_user_disputes.filter(status='resolved').count()
            context['count_closed'] = all_user_disputes.filter(status='closed').count()

            if status_filter and status_filter != 'all':
                if status_filter == 'review':
                    user_disputes = user_disputes.filter(status='investigating')
                else:
                    user_disputes = user_disputes.filter(status=status_filter)
            if q_filter:
                user_disputes = user_disputes.filter(
                    Q(ticket_id__icontains=q_filter) | Q(subject__icontains=q_filter)
                )

            context['complaints'] = user_disputes

        elif 'support/create-complaint' in path:
            if request.method == 'POST':
                related_item = request.POST.get('related_item', '')
                category = request.POST.get('category', 'quality')
                subject = request.POST.get('subject', '').strip()
                description = request.POST.get('description', '').strip()
                priority = request.POST.get('priority', 'medium').lower()
                evidence = request.FILES.get('evidence_image')

                job_obj = None
                qs_obj = None
                against_u = None

                if related_item:
                    if related_item.startswith('job:'):
                        j_id = related_item.split(':')[1]
                        job_obj = Job.objects.filter(id=j_id).first()
                        if job_obj:
                            if job_obj.assigned_vendor and job_obj.assigned_vendor != request.user:
                                against_u = job_obj.assigned_vendor
                            elif job_obj.user != request.user:
                                against_u = job_obj.user
                    elif related_item.startswith('qs:'):
                        q_id = related_item.split(':')[1]
                        qs_obj = QuickService.objects.filter(id=q_id).first()
                        if qs_obj:
                            selected_bid = Bid.objects.filter(quick_service=qs_obj, status='selected').first()
                            if selected_bid and selected_bid.vendor != request.user:
                                against_u = selected_bid.vendor
                            elif qs_obj.user != request.user:
                                against_u = qs_obj.user

                ticket = DisputeTicket.objects.create(
                    raised_by=request.user,
                    against_user=against_u,
                    job=job_obj,
                    quick_service=qs_obj,
                    category=category,
                    subject=subject,
                    description=description,
                    priority=priority,
                    evidence_image=evidence,
                    status='open'
                )
                return redirect(f'/user/support/complaint-details.html?id={ticket.id}')

            # GET: Load candidate jobs and quick services for the dropdown
            user_jobs = Job.objects.filter(user=request.user).order_by('-created_at')
            user_qs = ServiceBooking.objects.filter(customer=request.user).order_by('-created_at')
            context['user_jobs'] = user_jobs
            context['user_quick_services'] = user_qs

            preselected_job_id = request.GET.get('job_id')
            preselected_qs_id = request.GET.get('quick_service_id')
            if preselected_job_id:
                context['preselected_job'] = Job.objects.filter(id=preselected_job_id).first()
            if preselected_qs_id:
                context['preselected_qs'] = QuickService.objects.filter(id=preselected_qs_id).first()

        elif 'support/complaint-details' in path:
            ticket_id = request.GET.get('id') or request.GET.get('ticket_id')
            ticket = None
            if ticket_id:
                ticket_qs = DisputeTicket.objects.select_related(
                    'raised_by', 'against_user', 'job', 'quick_service', 'resolved_by'
                )
                if str(ticket_id).isdigit():
                    ticket = ticket_qs.filter(id=ticket_id).first()
                if not ticket:
                    ticket = ticket_qs.filter(ticket_id=ticket_id).first()

            if not ticket:
                return redirect('/user/support/complaints.html')

            if request.method == 'POST':
                action = request.POST.get('action')
                if action == 'add_response':
                    msg_text = request.POST.get('response', '').strip() or request.POST.get('message', '').strip()
                    extra_evidence = request.FILES.get('extra_evidence') or request.FILES.get('attachment')
                    if msg_text or extra_evidence:
                        DisputeMessage.objects.create(
                            ticket=ticket,
                            sender=request.user,
                            message=msg_text,
                            attachment=extra_evidence
                        )
                        if ticket.status == 'open':
                            ticket.status = 'investigating'
                            ticket.save()
                elif action == 'confirm_resolution':
                    ticket.status = 'resolved'
                    ticket.resolved_at = timezone.now()
                    ticket.resolved_by = request.user
                    ticket.save()

                return redirect(f'/user/support/complaint-details.html?id={ticket.id}')

            context['ticket'] = ticket
            context['messages'] = ticket.messages.select_related('sender').order_by('created_at')

    # ── AREA ADMIN COMPLAINTS & DISPUTES ──
    if ('complaints' in path or 'admin-dashboard/complaints' in path) and not path.startswith('user/'):
        admin_state, is_area_admin, available_states, co_admins = get_admin_state_context(request)
        context['admin_state'] = admin_state
        context['is_area_admin'] = is_area_admin

        disputes_qs = DisputeTicket.objects.select_related(
            'raised_by', 'against_user', 'job', 'quick_service', 'resolved_by'
        ).all().order_by('-created_at')

        if admin_state:
            disputes_qs = disputes_qs.filter(
                Q(job__location__state__iexact=admin_state) |
                Q(quick_service__location__state__iexact=admin_state) |
                Q(raised_by__assigned_state__iexact=admin_state) |
                Q(against_user__assigned_state__iexact=admin_state)
            )

        if 'details' in path:
            ticket_id = request.GET.get('id') or request.GET.get('ticket_id')
            ticket = None
            if ticket_id:
                if str(ticket_id).isdigit():
                    ticket = disputes_qs.filter(id=ticket_id).first()
                if not ticket:
                    ticket = disputes_qs.filter(ticket_id=ticket_id).first()

            if request.method == 'POST' and ticket:
                action = request.POST.get('action')
                if action == 'add_response':
                    msg_text = request.POST.get('message', '').strip()
                    attachment = request.FILES.get('attachment')
                    if msg_text or attachment:
                        DisputeMessage.objects.create(
                            ticket=ticket,
                            sender=request.user,
                            message=msg_text,
                            attachment=attachment
                        )
                        if ticket.status == 'open':
                            ticket.status = 'investigating'
                            ticket.save()
                elif action == 'update_status':
                    new_status = request.POST.get('status')
                    notes = request.POST.get('resolution_notes', '').strip()
                    if new_status in dict(DisputeTicket.STATUS_CHOICES):
                        ticket.status = new_status
                        if new_status in ['resolved', 'closed']:
                            ticket.resolved_by = request.user
                            ticket.resolved_at = timezone.now()
                    if notes:
                        ticket.resolution_notes = notes
                    ticket.save()
                return redirect(f'/complaints/details.html?id={ticket.id}')

            context['ticket'] = ticket
            if ticket:
                context['messages'] = ticket.messages.select_related('sender').order_by('created_at')
        else:
            q = request.GET.get('q', '').strip()
            status_filter = request.GET.get('status', '').strip()
            if q:
                disputes_qs = disputes_qs.filter(
                    Q(ticket_id__icontains=q) | Q(subject__icontains=q) |
                    Q(raised_by__username__icontains=q) | Q(against_user__username__icontains=q)
                )
            if status_filter:
                disputes_qs = disputes_qs.filter(status=status_filter)

            context['disputes'] = disputes_qs
            context['total_count'] = disputes_qs.count()
            context['open_count'] = disputes_qs.filter(status='open').count()
            context['review_count'] = disputes_qs.filter(status='investigating').count()
            context['resolved_count'] = disputes_qs.filter(status='resolved').count()
            context['closed_count'] = disputes_qs.filter(status='closed').count()

    # ── USER REVIEWS & RATINGS ──
    if 'reviews' in path and path.startswith('user/'):
        if not request.user.is_authenticated:
            return redirect('/login/?next=/' + path + '.html')

        if 'reviews/index' in path or path in ['user/reviews', 'user/reviews/index']:
            status_filter = request.GET.get('status')
            q_filter = request.GET.get('q', '').strip()

            all_reviews = ServiceReview.objects.filter(customer=request.user).select_related(
                'vendor', 'vendor__vendor_profile', 'job', 'quick_service'
            ).order_by('-created_at')

            reviews_list = all_reviews
            if status_filter and status_filter != 'all':
                reviews_list = reviews_list.filter(status=status_filter)
            if q_filter:
                reviews_list = reviews_list.filter(
                    Q(vendor__username__icontains=q_filter) |
                    Q(vendor__first_name__icontains=q_filter) |
                    Q(vendor__vendor_profile__company_name__icontains=q_filter) |
                    Q(job__title__icontains=q_filter) |
                    Q(quick_service__title__icontains=q_filter) |
                    Q(comment__icontains=q_filter) |
                    Q(review_title__icontains=q_filter)
                )

            total_count = all_reviews.count()
            published_count = all_reviews.filter(status='published').count()
            pending_count = all_reviews.filter(status='pending').count()
            avg_rating = 0.0
            if total_count > 0:
                from django.db.models import Avg
                agg_avg = all_reviews.aggregate(avg=Avg('rating'))['avg']
                avg_rating = round(agg_avg, 1) if agg_avg is not None else 5.0

            context['reviews'] = reviews_list
            context['total_reviews'] = total_count
            context['published_count'] = published_count
            context['pending_count'] = pending_count
            context['average_given_rating'] = avg_rating

        elif 'reviews/create' in path or path in ['user/reviews/create']:
            cand_jobs = Job.objects.filter(user=request.user, status__in=['selected', 'completed']).select_related('category', 'assigned_vendor', 'assigned_vendor__vendor_profile').order_by('-created_at')
            cand_qs = ServiceBooking.objects.filter(customer=request.user, status='completed').select_related('vendor', 'vendor__vendor_profile', 'quick_service', 'quick_service__category').order_by('-created_at')

            valid_cand_jobs = []
            for j in cand_jobs:
                vendor = j.assigned_vendor
                if not vendor:
                    sel = Bid.objects.filter(job=j, status__in=['selected', 'completed']).first()
                    if sel:
                        vendor = sel.vendor
                if vendor:
                    j.review_vendor = vendor
                    j.has_reviewed = ServiceReview.objects.filter(customer=request.user, job=j).exists()
                    valid_cand_jobs.append(j)

            valid_cand_qs = []
            for q in cand_qs:
                q.review_vendor = q.vendor
                q.has_reviewed = ServiceReview.objects.filter(booking=q).exists()
                valid_cand_qs.append(q)

            context['candidate_jobs'] = valid_cand_jobs
            context['candidate_quick_services'] = valid_cand_qs

            preselected_job_id = request.GET.get('job_id')
            preselected_qs_id = request.GET.get('booking_id') or request.GET.get('quick_service_id')
            preselected_vendor_id = request.GET.get('vendor_id')

            target_job = None
            target_qs = None
            target_vendor = None

            if preselected_job_id:
                target_job = Job.objects.filter(id=preselected_job_id, user=request.user).first()
                if target_job:
                    target_vendor = target_job.assigned_vendor
                    if not target_vendor:
                        sel = Bid.objects.filter(job=target_job, status__in=['selected', 'completed']).first()
                        if sel:
                            target_vendor = sel.vendor
            elif preselected_qs_id:
                target_qs = ServiceBooking.objects.filter(id=preselected_qs_id, customer=request.user, status='completed').select_related('vendor', 'vendor__vendor_profile', 'quick_service', 'quick_service__category').first()
                if target_qs:
                    target_vendor = target_qs.vendor

            if not target_vendor and preselected_vendor_id:
                target_vendor = User.objects.filter(id=preselected_vendor_id).first()

            context['preselected_job'] = target_job
            context['preselected_qs'] = target_qs
            context['preselected_vendor'] = target_vendor

    if path == 'user/profile/index' or path == 'user/profile':
        if request.user.is_authenticated:
            qs_count = ServiceBooking.objects.filter(customer=request.user).count()
            jobs_count = Job.objects.filter(user=request.user).count()
            completed_qs = ServiceBooking.objects.filter(customer=request.user, status='completed').count()
            completed_jobs = Job.objects.filter(user=request.user, status='completed').count()
            vendors_selected = Bid.objects.filter(Q(job__user=request.user) | Q(quick_service__vendor=request.user), status='selected').count()
            context.update({
                'qs_count': qs_count,
                'jobs_count': jobs_count,
                'completed_qs': completed_qs,
                'completed_jobs': completed_jobs,
                'vendors_selected': vendors_selected,
            })
            
    if path == 'user/profile/edit':
        if request.method == 'POST' and request.user.is_authenticated:
            first_name = request.POST.get('first_name')
            phone_number = request.POST.get('phone_number')
            email = request.POST.get('email')
            city = request.POST.get('city')
            state = request.POST.get('state')
            
            if first_name:
                request.user.first_name = first_name
            if email:
                request.user.email = email
            request.user.save()
            
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            if phone_number is not None:
                profile.phone_number = phone_number
            if city is not None:
                profile.city = city.strip()
                request.session['user_city'] = city.strip()
            if state is not None:
                profile.state = state.strip()
                request.session['user_state'] = state.strip()
            profile.save()
                
            return redirect('/user/profile/index.html')

    if path == 'vendor/profile/index' or path == 'vendor/profile':
        if request.user.is_authenticated:
            try:
                v_profile = request.user.vendor_profile
            except Exception:
                v_profile = None
            qs_count = ServiceBooking.objects.filter(vendor=request.user, status='completed').count()
            jobs_count = Job.objects.filter(bids__vendor=request.user, status='completed').distinct().count()
            total_bids = Bid.objects.filter(vendor=request.user).count()
            selected_bids = Bid.objects.filter(vendor=request.user, status='selected').count()
            context.update({
                'completed_qs': qs_count,
                'completed_jobs': jobs_count,
                'completed_jobs_count': jobs_count,
                'total_bids': total_bids,
                'total_bids_count': total_bids,
                'selected_bids_count': selected_bids,
                'profile': v_profile,
                'vendor_profile': v_profile,
            })

    if path in ['vendor/settings/security', 'vendor/settings/security.html']:
        if request.method == 'GET':
            return redirect('/vendor/settings/index.html#security')

    if path in ['vendor/settings', 'vendor/settings/index', 'vendor/settings/index.html'] or path.startswith('vendor/settings'):
        if not request.user.is_authenticated:
            return redirect('/login/?next=/vendor/settings/index.html')
            
        v_prof, _ = VendorProfile.objects.get_or_create(user=request.user)
        u_prof, _ = UserProfile.objects.get_or_create(user=request.user)
        
        if request.method == 'POST':
            active_tab = request.POST.get('active_tab', '')
            if 'security' in path or active_tab == 'security':
                from django.contrib.auth import update_session_auth_hash
                current_pwd = request.POST.get('current_password', '')
                new_pwd = request.POST.get('new_password', '')
                confirm_pwd = request.POST.get('confirm_password', '')
                
                if not current_pwd or not new_pwd or not confirm_pwd:
                    messages.error(request, "All password fields are required.")
                elif not request.user.check_password(current_pwd):
                    messages.error(request, "Current password is incorrect.")
                elif new_pwd != confirm_pwd:
                    messages.error(request, "New passwords do not match.")
                elif len(new_pwd) < 8:
                    messages.error(request, "New password must be at least 8 characters long.")
                else:
                    request.user.set_password(new_pwd)
                    request.user.save()
                    update_session_auth_hash(request, request.user)
                    messages.success(request, "Password updated successfully!")
                return redirect('/vendor/settings/index.html#security')
            elif active_tab == 'profile':
                save_vendor_profile_changes(request, request.user)
                messages.success(request, "Business profile & branding updated successfully!")
                return redirect('/vendor/settings/index.html#profile')
            elif active_tab == 'account':
                save_vendor_profile_changes(request, request.user)
                messages.success(request, "Account details and contact information updated successfully!")
                return redirect('/vendor/settings/index.html#account')
            elif active_tab == 'notifications':
                messages.success(request, "Notification preferences updated successfully!")
                return redirect('/vendor/settings/index.html#notifications')
            else:
                save_vendor_profile_changes(request, request.user)
                messages.success(request, "Settings updated successfully!")
                return redirect('/vendor/settings/index.html')

    if path in ['vendor/profile/edit', 'vendor/profile/edit.html']:
        if not request.user.is_authenticated:
            return redirect('/login/?next=/vendor/profile/edit.html')
        if request.method == 'POST':
            save_vendor_profile_changes(request, request.user)
            messages.success(request, "Profile updated successfully!")
            return redirect('/vendor/profile/index.html')

    if path.startswith('vendor/kyc'):
        return redirect('/vendor/dashboard.html')

    if path in ['vendor/wallet/index', 'vendor/wallet', 'vendor/wallet.html']:
        from .wallet_services import get_or_create_wallet, request_payout, get_platform_commission_percent, settle_job_completion
        
        if not request.user.is_authenticated:
            return redirect('/login/?next=/vendor/wallet/index.html')
            
        wallet = get_or_create_wallet(request.user)
        context['wallet'] = wallet
        context['commission_percent'] = get_platform_commission_percent()

        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'request_payout':
                amt_str = request.POST.get('amount', '').strip()
                payout_method = request.POST.get('payout_method', 'bank')
                account_holder_name = request.POST.get('account_holder_name', '').strip()
                account_number = request.POST.get('account_number', '').strip()
                confirm_account_number = request.POST.get('confirm_account_number', '').strip()
                ifsc_code = request.POST.get('ifsc_code', '').strip().upper()
                bank_name = request.POST.get('bank_name', '').strip()
                upi_id = request.POST.get('upi_id', '').strip()

                if payout_method == 'bank' and account_number and confirm_account_number and account_number != confirm_account_number:
                    context['error_message'] = "Account numbers do not match. Please verify and try again."
                else:
                    try:
                        amt = float(amt_str)
                        ok, res = request_payout(
                            vendor=request.user,
                            amount=amt,
                            payout_method=payout_method,
                            account_holder_name=account_holder_name,
                            account_number=account_number,
                            ifsc_code=ifsc_code,
                            bank_name=bank_name,
                            upi_id=upi_id
                        )
                        if ok:
                            context['success_message'] = f"Payout request for ₹{amt:.2f} submitted successfully! We will process the transfer shortly."
                            wallet.refresh_from_db()
                            context['wallet'] = wallet
                            context['wallet_balance'] = f"{wallet.available_balance:.2f}"
                        else:
                            context['error_message'] = str(res)
                    except (ValueError, TypeError):
                        context['error_message'] = "Please enter a valid numeric withdrawal amount."

        # Fetch itemized transactions & payout requests
        context['transactions'] = wallet.transactions.all().order_by('-created_at')[:50]
        context['payout_requests'] = PayoutRequest.objects.filter(vendor=request.user).order_by('-requested_at')[:50]
        context['pending_payouts_sum'] = PayoutRequest.objects.filter(vendor=request.user, status='pending').aggregate(total=Sum('amount'))['total'] or 0
        context['wallet_balance'] = f"{wallet.available_balance:.2f}"

    if path == 'vendor/jobs/available':
        jobs_qs = Job.objects.filter(status='open').select_related('category', 'location', 'user').order_by('-created_at')
        
        vendor_city = None
        vendor_categories = []
        if request.user.is_authenticated:
            v_prof = getattr(request.user, 'vendor_profile', None)
            if not v_prof and getattr(request.user, 'role', '') == 'VENDOR':
                v_prof, _ = VendorProfile.objects.get_or_create(user=request.user)
            if v_prof:
                if v_prof.location and v_prof.location.strip():
                    vendor_city = v_prof.location.strip().split(',')[0].strip()
                elif getattr(v_prof, 'address', None):
                    vendor_city = v_prof.address.strip().split(',')[0].strip()
                if v_prof.category and v_prof.category.strip():
                    vendor_categories = v_prof.categories_list
                
        if vendor_city:
            city_filter = (
                Q(location__city__iexact=vendor_city) |
                Q(city__iexact=vendor_city) |
                (Q(location__isnull=True) & (Q(address__icontains=vendor_city) | Q(locality__icontains=vendor_city)))
            )
            jobs_qs = jobs_qs.filter(city_filter)
            context['vendor_city'] = vendor_city
            context['vendor_location'] = vendor_city
        else:
            context.setdefault('vendor_city', context.get('vendor_location') or 'Ranchi')
            context.setdefault('vendor_location', context.get('vendor_city') or 'Ranchi')

        if vendor_categories:
            cat_filter = Q()
            has_general = any(c.lower() in ['other', 'general', 'other / general services', 'general services'] for c in vendor_categories)
            if has_general:
                cat_filter |= Q(category__isnull=True) | Q(category__name__icontains='General') | Q(category__name__icontains='Other')
            
            for cat_name in vendor_categories:
                if cat_name.lower() not in ['other', 'general', 'other / general services', 'general services']:
                    cat_filter |= (
                        Q(category__name__iexact=cat_name) |
                        Q(category__name__icontains=cat_name) |
                        (Q(category__isnull=True) & Q(title__icontains=cat_name))
                    )
            jobs_qs = jobs_qs.filter(cat_filter)
            context['vendor_categories'] = vendor_categories

        context['available_jobs'] = jobs_qs
        context['all_categories'] = Category.objects.filter(status='active').order_by('name')

    if path == 'vendor/quick-services/nearby':
        return redirect('/vendor/catalog/index.html')

    if path == 'vendor/quick-services/details':
        qs_id = request.GET.get('id')
        if qs_id:
            try:
                qs = QuickService.objects.select_related('category', 'location', 'vendor').get(id=qs_id)
                qs.budget = float(qs.base_price)
                context['qs'] = qs
            except QuickService.DoesNotExist:
                return redirect('/vendor/catalog/index.html')

    if path == 'vendor/quick-services/send-quotation':
        qs_id = request.GET.get('qs_id') or request.GET.get('id') or request.POST.get('qs_id') or request.POST.get('id')
        if qs_id:
            try:
                qs = QuickService.objects.select_related('category', 'location', 'vendor').get(id=qs_id)
                qs.budget = float(qs.base_price)
                context['qs'] = qs
                
                if request.method == 'POST' and request.user.is_authenticated:
                    amount = request.POST.get('amount')
                    estimated_time = request.POST.get('estimated_time')
                    proposal = request.POST.get('proposal')
                    attachment = request.FILES.get('attachment')
                    if amount:
                        Bid.objects.create(
                            vendor=request.user,
                            quick_service=qs,
                            amount=float(amount),
                            estimated_time=estimated_time,
                            proposal=proposal,
                            attachment=attachment,
                            status='submitted'
                        )
                        messages.success(request, f"Quotation for '{qs.title}' submitted successfully!")
                        return redirect('/vendor/jobs/available.html')
            except QuickService.DoesNotExist:
                return redirect('/vendor/catalog/index.html')

    if path == 'vendor/jobs/bid-details':
        bid_id = request.GET.get('bid_id')
        if bid_id:
            try:
                bid = Bid.objects.select_related('job', 'job__user').get(id=bid_id, vendor=request.user)
                context['bid'] = bid
            except Bid.DoesNotExist:
                pass

    if path == 'vendor/jobs/selected-jobs':
        selected_bids = Bid.objects.filter(vendor=request.user, status__in=['selected', 'completed']).select_related('job', 'quick_service', 'job__user', 'quick_service__vendor').order_by('-created_at')
        context['selected_bids'] = selected_bids

    if path == 'vendor/jobs/details' or path == 'vendor/jobs/send-quotation':
        job_id = request.GET.get('id') or request.GET.get('job_id') or request.POST.get('job_id') or request.POST.get('id')
        
        gs_obj = GlobalSettings.objects.first()
        comm_pct = Decimal(str(gs_obj.platform_commission_percent if gs_obj and gs_obj.platform_commission_percent is not None else '10.00'))
        cgst_pct = Decimal(str(gs_obj.cgst_percent if gs_obj and gs_obj.cgst_percent is not None else '9.00'))
        sgst_pct = Decimal(str(gs_obj.sgst_percent if gs_obj and gs_obj.sgst_percent is not None else '9.00'))
        flat_fee = Decimal(str(gs_obj.platform_flat_fee if gs_obj and gs_obj.platform_flat_fee is not None else '0.00'))
        tax_mode = gs_obj.tax_calculation_mode if gs_obj and gs_obj.tax_calculation_mode else 'commission_only'

        context['platform_commission_percent'] = float(comm_pct)
        context['cgst_percent'] = float(cgst_pct)
        context['sgst_percent'] = float(sgst_pct)
        context['platform_flat_fee'] = float(flat_fee)
        context['tax_calculation_mode'] = tax_mode

        if path == 'vendor/jobs/send-quotation' and request.method == 'POST' and request.user.is_authenticated:
            amount = request.POST.get('amount')
            estimated_time = request.POST.get('estimated_time')
            proposal = request.POST.get('proposal')
            attachment = request.FILES.get('attachment')
            
            if job_id and amount:
                try:
                    job = Job.objects.get(id=job_id)
                    amount_float = float(amount)
                    
                    # Validate bidding limits set by Superadmin
                    is_limit_reached = bool(job.max_bids and job.bids.count() >= job.max_bids)
                    below_min = bool(job.min_bid_amount and amount_float < float(job.min_bid_amount))
                    above_max = bool(job.max_bid_amount and amount_float > float(job.max_bid_amount))
                    is_open = job.status == 'open'
                    
                    if not is_limit_reached and not below_min and not above_max and is_open:
                        vp = getattr(request.user, 'vendor_profile', None)
                        if vp and (vp.available_bids or 0) > 0:
                            if not Bid.objects.filter(job=job, vendor=request.user).exists():
                                # Itemized Financial Computation
                                vendor_base = Decimal(str(amount_float)).quantize(Decimal('0.01'))
                                comm_amount = ((vendor_base * comm_pct) / Decimal('100.00') + flat_fee).quantize(Decimal('0.01'))

                                if tax_mode == 'commission_only':
                                    cgst_amount = ((comm_amount * cgst_pct) / Decimal('100.00')).quantize(Decimal('0.01'))
                                    sgst_amount = ((comm_amount * sgst_pct) / Decimal('100.00')).quantize(Decimal('0.01'))
                                else:
                                    taxable_base = vendor_base + comm_amount
                                    cgst_amount = ((taxable_base * cgst_pct) / Decimal('100.00')).quantize(Decimal('0.01'))
                                    sgst_amount = ((taxable_base * sgst_pct) / Decimal('100.00')).quantize(Decimal('0.01'))

                                total_customer = (vendor_base + comm_amount + cgst_amount + sgst_amount).quantize(Decimal('0.01'))

                                Bid.objects.create(
                                    vendor=request.user,
                                    job=job,
                                    amount=total_customer,
                                    vendor_base_amount=vendor_base,
                                    commission_percent_applied=comm_pct,
                                    commission_amount=comm_amount,
                                    cgst_percent_applied=cgst_pct,
                                    cgst_amount=cgst_amount,
                                    sgst_percent_applied=sgst_pct,
                                    sgst_amount=sgst_amount,
                                    flat_fee_amount=flat_fee,
                                    total_customer_amount=total_customer,
                                    estimated_time=estimated_time,
                                    proposal=proposal,
                                    attachment=attachment
                                )
                                vp.available_bids = int(vp.available_bids or 0) - 1
                                vp.save(update_fields=['available_bids'])

                                # Record dynamic credit transaction
                                BidCreditTransaction.objects.create(
                                    vendor=request.user,
                                    transaction_type='used',
                                    credits=-1,
                                    description=f"Bid placed on {job.title}",
                                    related_job=job
                                )
                                messages.success(request, f"Quotation submitted successfully! 1 credit deducted ({vp.available_bids} credits remaining).")
                        else:
                            messages.error(request, "Insufficient bid credits! You have 0 credits left. Please purchase a bid package.")
                except (Job.DoesNotExist, ValueError, TypeError):
                    pass
            # Let the script handle the success state, or reload if JS doesn't prevent default
            
        if job_id:
            try:
                job = Job.objects.select_related('category', 'location', 'user').get(id=job_id)
                context['job'] = job
                
                if request.user.is_authenticated:
                    has_bid = Bid.objects.filter(job=job, vendor=request.user).exists()
                    context['has_bid'] = has_bid
            except Job.DoesNotExist:
                return redirect('/vendor/jobs/available.html')
        else:
            return redirect('/vendor/jobs/available.html')

    if path in ['vendor/catalog', 'vendor/catalog/index', 'vendor/catalog/index.html']:
        if request.user.is_authenticated:
            srv_qs = QuickService.objects.filter(vendor=request.user).select_related('category').order_by('-created_at')
            context['my_services'] = srv_qs
            context['categories'] = Category.objects.filter(status='active').order_by('name')
            gs = GlobalSettings.objects.first()
            context['global_settings'] = gs
            services_data = {}
            for s in srv_qs:
                services_data[str(s.id)] = {
                    'id': s.id,
                    'title': s.title,
                    'category_id': s.category_id or '',
                    'category_name': s.category.name if s.category else '',
                    'status': s.status,
                    'description': s.description or '',
                    'locality': s.locality or '',
                    'service_radius_km': float(s.service_radius_km or 10.0),
                    'latitude': float(s.latitude) if s.latitude else None,
                    'longitude': float(s.longitude) if s.longitude else None,
                    'image_url': s.image.url if s.image else (s.image_url or ''),
                    'packages': s.service_packages or [],
                    'inclusions': s.inclusions or [],
                    'exclusions': s.exclusions or [],
                    'base_price': float(s.base_price or 199.0),
                }
            context['my_services_json'] = json.dumps(services_data)

    if path in ['vendor/bookings', 'vendor/bookings/index', 'vendor/bookings/index.html']:
        if request.method == 'POST' and request.user.is_authenticated:
            booking_id = request.POST.get('booking_id')
            action = request.POST.get('action') # e.g. accept, complete, cancel
            if booking_id and action:
                try:
                    booking = ServiceBooking.objects.get(id=booking_id, vendor=request.user)
                    if action == 'accept':
                        booking.status = 'accepted'
                        booking.save(update_fields=['status'])
                        messages.success(request, f"Booking #{booking.id} accepted.")
                    elif action == 'complete':
                        if booking.payment_status != 'paid':
                            gs = GlobalSettings.objects.first()
                            base_amt = float(booking.total_amount or 0.0) + float(booking.additional_charges or 0.0)
                            calc = gs.split_qs_final_total(base_amt) if gs else {'vendor_payout': base_amt, 'commission': 0, 'cgst': 0, 'sgst': 0, 'flat_fee': 0, 'customer_price': base_amt}

                            vendor_payout = Decimal(str(calc['vendor_payout'])).quantize(Decimal('0.01'))
                            platform_comm = Decimal(str(calc['commission'])).quantize(Decimal('0.01'))
                            cgst = Decimal(str(calc['cgst'])).quantize(Decimal('0.01'))
                            sgst = Decimal(str(calc['sgst'])).quantize(Decimal('0.01'))
                            flat_fee = Decimal(str(calc['flat_fee'])).quantize(Decimal('0.01'))
                            total_cust = Decimal(str(calc['customer_price'])).quantize(Decimal('0.01'))

                            booking.status = 'completed'
                            booking.payment_status = 'paid'
                            booking.payment_method = request.POST.get('payment_method') or 'upi_qr'
                            booking.completed_at = timezone.now()
                            booking.save(update_fields=['status', 'payment_status', 'payment_method', 'completed_at'])

                            # Credit Vendor Wallet
                            vw, _ = VendorWallet.objects.get_or_create(vendor=booking.vendor)
                            vw.available_balance = (vw.available_balance or Decimal('0.00')) + vendor_payout
                            vw.total_earned = (vw.total_earned or Decimal('0.00')) + vendor_payout
                            vw.save(update_fields=['available_balance', 'total_earned', 'updated_at'])

                            WalletTransaction.objects.create(
                                wallet=vw,
                                amount=vendor_payout,
                                transaction_type='credit',
                                related_quick_service=booking.quick_service,
                                description=f"Earnings for Booking #{booking.id}: {booking.package_name}"
                            )

                            PlatformRevenueLedger.objects.create(
                                related_booking=booking,
                                related_quick_service=booking.quick_service,
                                vendor=booking.vendor,
                                vendor_payout=vendor_payout,
                                platform_commission=platform_comm,
                                cgst_collected=cgst,
                                sgst_collected=sgst,
                                flat_fee_collected=flat_fee,
                                total_customer_paid=total_cust,
                                settled_at=timezone.now()
                            )
                            messages.success(request, f"Booking #{booking.id} completed! ₹{float(vendor_payout):,.2f} credited to your wallet.")
                        else:
                            booking.status = 'completed'
                            booking.save(update_fields=['status'])
                            messages.success(request, f"Booking #{booking.id} marked as completed.")
                    elif action == 'cancel':
                        booking.status = 'cancelled'
                        booking.save(update_fields=['status'])
                        messages.success(request, f"Booking #{booking.id} has been declined.")
                except ServiceBooking.DoesNotExist:
                    pass
            return redirect('/vendor/bookings/index.html')

        if request.user.is_authenticated:
            v_bookings = ServiceBooking.objects.filter(vendor=request.user).select_related('customer', 'quick_service', 'quick_service__category').order_by('-created_at')
            enhanced_v_bookings = []
            for b in v_bookings:
                lat, lng = None, None
                clean_addr = b.service_address or ''
                if b.service_address:
                    m = re.search(r'\[GPS:\s*([-\d.]+),\s*([-\d.]+)', b.service_address)
                    if m:
                        lat, lng = m.group(1), m.group(2)
                    clean_addr = re.sub(r'\[GPS:[^\]]+\]', '', b.service_address).strip()
                if lat and lng:
                    map_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
                elif clean_addr:
                    map_url = f"https://www.google.com/maps/search/?api=1&query={clean_addr.replace(' ', '+')}"
                else:
                    map_url = ""
                cust_phone = ''
                if hasattr(b.customer, 'user_profile') and b.customer.user_profile and b.customer.user_profile.phone_number:
                    cust_phone = b.customer.user_profile.phone_number
                elif hasattr(b.customer, 'phone_number'):
                    cust_phone = b.customer.phone_number or ''
                # PRIVACY: hide customer identity & location until the vendor accepts
                b.contact_locked = b.status not in ('accepted', 'completed')
                if b.contact_locked:
                    lat = lng = None
                    clean_addr = ''
                    map_url = ''
                    cust_phone = ''
                b.latitude = lat
                b.longitude = lng
                b.clean_address = clean_addr
                b.map_url = map_url
                b.customer_phone = cust_phone or '—'
                enhanced_v_bookings.append(b)
            context['my_bookings'] = enhanced_v_bookings
    if path in ['user/services/browse', 'user/services/browse.html']:
        context['services'] = QuickService.objects.filter(status='active').select_related('vendor', 'vendor__vendor_profile', 'category', 'location').order_by('-created_at')
        context['categories'] = Category.objects.filter(status='active')

    if path in ['user/services/detail', 'user/services/detail.html']:
        qs_id = request.GET.get('id') or request.GET.get('service_id')
        if qs_id:
            try:
                service = QuickService.objects.select_related('vendor', 'vendor__vendor_profile', 'category', 'location').get(id=qs_id)
                context['service'] = service
                
                # Fetch published reviews for this service or vendor
                reviews = ServiceReview.objects.filter(
                    Q(quick_service=service) | Q(vendor=service.vendor),
                    status='published'
                ).select_related('customer').order_by('-created_at')[:8]
                context['reviews'] = reviews
                
                review_count = reviews.count()
                avg_rating = 4.9
                if review_count > 0:
                    total_stars = sum([r.rating for r in reviews])
                    avg_rating = round(total_stars / review_count, 1)
                context['avg_rating'] = avg_rating
                context['review_count'] = review_count

                # Related services in same category
                context['related_services'] = QuickService.objects.filter(
                    category=service.category, status='active'
                ).exclude(id=service.id).select_related('vendor', 'vendor__vendor_profile')[:3]
            except QuickService.DoesNotExist:
                return redirect('/user/services/browse.html')
        else:
            return redirect('/user/services/browse.html')

    if path in ['user/services/book', 'user/services/book.html']:
        if request.method == 'POST' and request.user.is_authenticated:
            qs_id = request.POST.get('qs_id')
            package_name = request.POST.get('package_name', 'Base Service')
            total_amount = request.POST.get('total_amount', 0)
            scheduled_date = request.POST.get('scheduled_date')
            scheduled_time = request.POST.get('scheduled_time', '').strip() or None
            
            # Combine full structured address and GPS coordinates
            service_address = request.POST.get('service_address', '').strip()
            house_no = request.POST.get('house_no', '').strip()
            street = request.POST.get('street', '').strip()
            landmark = request.POST.get('landmark', '').strip()
            city = request.POST.get('city', '').strip()
            pincode = request.POST.get('pincode', '').strip()
            lat = request.POST.get('latitude', '').strip()
            lng = request.POST.get('longitude', '').strip()

            if not service_address and (house_no or street):
                addr_parts = [p for p in [house_no, street, landmark, city, pincode] if p]
                service_address = ", ".join(addr_parts)

            if lat and lng and '[GPS:' not in service_address:
                service_address = f"{service_address} [GPS: {lat}, {lng} | https://maps.google.com/?q={lat},{lng}]".strip()

            if qs_id and scheduled_date and service_address:
                try:
                    qs = QuickService.objects.select_related('vendor', 'vendor__vendor_profile').get(id=qs_id)
                    if hasattr(qs.vendor, 'vendor_profile') and not qs.vendor.vendor_profile.is_online:
                        messages.error(request, "This vendor is currently offline and not accepting bookings.")
                        return redirect(f'/user/services/detail.html?id={qs_id}')
                        
                    ServiceBooking.objects.create(
                        customer=request.user,
                        vendor=qs.vendor,
                        quick_service=qs,
                        package_name=package_name,
                        total_amount=total_amount,
                        scheduled_date=scheduled_date,
                        scheduled_time=scheduled_time,
                        service_address=service_address,
                        status='pending'
                    )
                    messages.success(request, f"Service '{qs.title}' booked successfully! Awaiting vendor acceptance.")
                    return redirect('/user/services/my-bookings.html')
                except QuickService.DoesNotExist:
                    pass

        qs_id = request.GET.get('id') or request.GET.get('service_id')
        if qs_id:
            try:
                service = QuickService.objects.select_related('vendor', 'vendor__vendor_profile', 'category', 'location').get(id=qs_id)
                context['service'] = service
                context['selected_pkg'] = request.GET.get('pkg', 'Base Service')
                context['selected_amount'] = request.GET.get('amount', str(service.base_price))
                if request.user.is_authenticated:
                    context['user_addresses'] = CustomerAddress.objects.filter(user=request.user)
            except QuickService.DoesNotExist:
                return redirect('/user/services/browse.html')
        else:
            return redirect('/user/services/browse.html')

    if path in ['user/services/my-bookings', 'user/services/my-bookings.html']:
        if request.user.is_authenticated:
            c_bookings = ServiceBooking.objects.filter(customer=request.user).select_related(
                'vendor', 'vendor__vendor_profile', 'quick_service', 'quick_service__category', 'review'
            ).order_by('-created_at')
            enhanced_c_bookings = []
            for b in c_bookings:
                lat, lng = None, None
                clean_addr = b.service_address or ''
                if b.service_address:
                    m = re.search(r'\[GPS:\s*([-\d.]+),\s*([-\d.]+)', b.service_address)
                    if m:
                        lat, lng = m.group(1), m.group(2)
                    clean_addr = re.sub(r'\[GPS:[^\]]+\]', '', b.service_address).strip()
                if lat and lng:
                    map_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
                elif clean_addr:
                    map_url = f"https://www.google.com/maps/search/?api=1&query={clean_addr.replace(' ', '+')}"
                else:
                    map_url = ""

                v_phone = ''
                if hasattr(b.vendor, 'user_profile') and b.vendor.user_profile and b.vendor.user_profile.phone_number:
                    v_phone = b.vendor.user_profile.phone_number
                elif hasattr(b.vendor, 'vendor_profile') and b.vendor.vendor_profile:
                    v_phone = getattr(b.vendor.vendor_profile, 'phone_number', '') or getattr(b.vendor.vendor_profile, 'emergency_contact', '')
                if not v_phone and hasattr(b.vendor, 'phone_number'):
                    v_phone = b.vendor.phone_number

                v_company = ''
                if hasattr(b.vendor, 'vendor_profile') and b.vendor.vendor_profile:
                    v_company = b.vendor.vendor_profile.company_name or ''

                b.latitude = lat
                b.longitude = lng
                b.clean_address = clean_addr
                b.map_url = map_url
                b.vendor_phone = v_phone or '—'
                b.vendor_company = v_company or b.vendor.get_full_name() or b.vendor.username
                b.user_review = getattr(b, 'review', None)
                enhanced_c_bookings.append(b)
            context['my_bookings'] = enhanced_c_bookings

    if 'master/locations' in path:
        admin_state, is_area_admin, available_states, co_admins = get_admin_state_context(request)
        if admin_state:
            context['locations'] = Location.objects.filter(state__iexact=admin_state).order_by('-created_at')
        else:
            context['locations'] = Location.objects.all().order_by('-created_at')
        context['states'] = available_states
        context['admin_state'] = admin_state
        context['is_area_admin'] = is_area_admin
        
    if 'users/users' in path or 'users/customers' in path or 'users/vendors' in path or 'users/company-vendors' in path or 'users/outsider-vendors' in path or 'users/user-details' in path or 'users/vendor-details' in path:
        admin_state, is_area_admin, available_states, co_admins = get_admin_state_context(request)
        context['admin_state'] = admin_state
        context['is_area_admin'] = is_area_admin

        if 'users/user-details' in path:
            uid_raw = request.GET.get('id') or ''
            target_uid = None
            if uid_raw:
                digits = ''.join([c for c in str(uid_raw) if c.isdigit()])
                if digits:
                    target_uid = int(digits)

            target_user = None
            if target_uid:
                target_user = User.objects.filter(id=target_uid, role='USER').select_related('user_profile').first()
            if not target_user:
                cust_qs = User.objects.filter(role='USER')
                if admin_state:
                    job_uids = Job.objects.filter(Q(location__state__iexact=admin_state) | Q(address__icontains=admin_state)).values_list('user_id', flat=True)
                    qs_uids = QuickService.objects.filter(Q(location__state__iexact=admin_state) | Q(locality__icontains=admin_state)).values_list('vendor_id', flat=True)
                    cust_qs = cust_qs.filter(Q(id__in=set(job_uids).union(set(qs_uids))) | Q(assigned_state__iexact=admin_state))
                target_user = cust_qs.first()

            if target_user:
                # Strict territory authorization check for Area Admin
                if is_area_admin and admin_state:
                    user_matches_state = bool(target_user.assigned_state and target_user.assigned_state.lower() == admin_state.lower())
                    has_job_in_state = Job.objects.filter(user=target_user).filter(Q(location__state__iexact=admin_state) | Q(address__icontains=admin_state)).exists()
                    has_qs_in_state = ServiceBooking.objects.filter(customer=target_user).filter(Q(quick_service__location__state__iexact=admin_state) | Q(service_address__icontains=admin_state)).exists()

                    if not (user_matches_state or has_job_in_state or has_qs_in_state):
                        messages.error(request, f"Access Denied: Customer '{target_user.get_full_name() or target_user.username}' is outside your assigned territory ({admin_state}).")
                        return redirect('/admin-dashboard/users/users.html')

                mobile = '—'
                try:
                    if hasattr(target_user, 'user_profile') and target_user.user_profile.phone_number:
                        mobile = target_user.user_profile.phone_number
                except Exception:
                    pass

                cust_qs_list = ServiceBooking.objects.filter(customer=target_user).select_related('quick_service', 'vendor').order_by('-created_at')
                cust_jobs_list = Job.objects.filter(user=target_user).select_related('category', 'location').order_by('-created_at')
                if admin_state:
                    cust_qs_list = cust_qs_list.filter(Q(quick_service__location__state__iexact=admin_state) | Q(service_address__icontains=admin_state))
                    cust_jobs_list = cust_jobs_list.filter(Q(location__state__iexact=admin_state) | Q(address__icontains=admin_state))

                completed_jobs = cust_jobs_list.filter(status='completed').count()

                cust_data = {
                    'id': f'USR-{target_user.id:04d}',
                    'name': target_user.get_full_name() or target_user.username,
                    'email': target_user.email or '—',
                    'mobile': mobile,
                    'location': target_user.assigned_state or (admin_state or 'Unknown'),
                    'quickServices': cust_qs_list.count(),
                    'jobs': cust_jobs_list.count(),
                    'completedJobs': completed_jobs,
                    'status': 'active' if target_user.is_active else 'suspended',
                    'registered': target_user.date_joined.strftime('%Y-%m-%d') if target_user.date_joined else 'Unknown'
                }

                qs_items = []
                for s in cust_qs_list:
                    qs_items.append({
                        'id': f'QS-{s.id:04d}',
                        'title': s.title,
                        'category': s.category.name if s.category else 'General',
                        'budget': float(s.budget) if s.budget else 0,
                        'status': s.status,
                        'created': s.created_at.strftime('%Y-%m-%d') if s.created_at else 'Unknown'
                    })

                job_items = []
                for j in cust_jobs_list:
                    bids_cnt = Bid.objects.filter(job=j).count()
                    loc_str = f"{j.location.city}, {j.location.state}" if j.location else (admin_state or 'Unknown')
                    job_items.append({
                        'id': f'JOB-{j.id:04d}',
                        'title': j.title,
                        'location': loc_str,
                        'budget': float(j.budget) if j.budget else 0,
                        'bids': bids_cnt,
                        'status': j.status,
                        'created': j.created_at.strftime('%Y-%m-%d') if j.created_at else 'Unknown'
                    })

                context['customer_json'] = json.dumps(cust_data)
                context['customer_qs_json'] = json.dumps(qs_items)
                context['customer_jobs_json'] = json.dumps(job_items)
                context['customer_reviews_json'] = json.dumps([])
                context['customer_complaints_json'] = json.dumps([])
                context['target_user'] = target_user

        elif 'users/vendor-details' in path:
            vid_raw = request.GET.get('id') or ''
            target_vid = None
            if vid_raw:
                digits = ''.join([c for c in str(vid_raw) if c.isdigit()])
                if digits:
                    target_vid = int(digits)

            target_vendor = None
            if target_vid:
                target_vendor = VendorProfile.objects.select_related('user').filter(Q(id=target_vid) | Q(user_id=target_vid)).first()

            if not target_vendor:
                v_qs = VendorProfile.objects.select_related('user').all()
                if admin_state:
                    v_qs = v_qs.filter(Q(location__icontains=admin_state) | Q(user__assigned_state__iexact=admin_state))
                target_vendor = v_qs.first()

            if target_vendor:
                # Strict territory authorization check for Area Admin
                if is_area_admin and admin_state:
                    vendor_in_state = (admin_state.lower() in (target_vendor.location or '').lower()) or (bool(target_vendor.user.assigned_state and target_vendor.user.assigned_state.lower() == admin_state.lower()))
                    if not vendor_in_state:
                        messages.error(request, f"Access Denied: Vendor '{target_vendor}' is outside your assigned territory ({admin_state}).")
                        return redirect('/admin-dashboard/users/vendors.html')

                u = target_vendor.user
                total_bids = Bid.objects.filter(vendor=u)
                if admin_state:
                    total_bids = total_bids.filter(Q(job__location__state__iexact=admin_state) | Q(quick_service__location__state__iexact=admin_state) | Q(job__address__icontains=admin_state) | Q(quick_service__locality__icontains=admin_state))

                successful_bids = total_bids.filter(status='selected').count()
                completed_jobs = Job.objects.filter(bids__vendor=u, status='completed').distinct()
                if admin_state:
                    completed_jobs = completed_jobs.filter(Q(location__state__iexact=admin_state) | Q(address__icontains=admin_state))

                active_jobs = Job.objects.filter(bids__vendor=u, status__in=['open', 'progress', 'selected']).distinct()
                if admin_state:
                    active_jobs = active_jobs.filter(Q(location__state__iexact=admin_state) | Q(address__icontains=admin_state))

                vendor_contact = '—'
                try:
                    if hasattr(u, 'user_profile') and u.user_profile.phone_number:
                        vendor_contact = u.user_profile.phone_number
                except Exception:
                    pass

                vendor_data = {
                    'id': f'VEN-{u.id:04d}',
                    'name': target_vendor.company_name or u.get_full_name() or u.username,
                    'email': u.email or '—',
                    'type': target_vendor.vendor_type,
                    'contact': vendor_contact,
                    'category': target_vendor.category or 'Uncategorized',
                    'location': target_vendor.location or (admin_state or 'Unknown'),
                    'totalBids': total_bids.count(),
                    'successfulBids': successful_bids,
                    'withdrawnBids': 0,
                    'rejectedBids': total_bids.filter(status='rejected').count(),
                    'completedJobs': completed_jobs.count(),
                    'activeJobs': active_jobs.count(),
                    'bidCredits': getattr(target_vendor, 'bid_credits', 100),
                    'rating': float(target_vendor.rating or 4.5),
                    'status': 'active' if u.is_active else 'suspended',
                    'registered': target_vendor.registered_date.strftime('%Y-%m-%d') if target_vendor.registered_date else 'Unknown'
                }

                bids_list = []
                for b in total_bids.select_related('job', 'quick_service'):
                    target_item = b.job or b.quick_service
                    bids_list.append({
                        'id': f'BID-{b.id:04d}',
                        'jobId': f'JOB-{b.job.id:04d}' if b.job else (f'QS-{b.quick_service.id:04d}' if b.quick_service else '—'),
                        'vendorId': f'VEN-{u.id:04d}',
                        'job': target_item.title if target_item else 'Service',
                        'amount': float(b.amount),
                        'status': b.status,
                        'created': b.created_at.strftime('%Y-%m-%d') if b.created_at else 'Unknown'
                    })

                purchases_list = []
                for sub in Subscription.objects.filter(vendor=u).order_by('-created_at'):
                    purchases_list.append({
                        'id': f'TXN-{sub.id:04d}',
                        'package': sub.package_name,
                        'amount': float(sub.amount),
                        'paymentStatus': sub.status,
                        'date': sub.created_at.strftime('%Y-%m-%d') if sub.created_at else 'Unknown'
                    })

                context['vendor_json'] = json.dumps(vendor_data)
                context['vendor_bids_json'] = json.dumps(bids_list)
                context['vendor_jobs_json'] = json.dumps([])
                context['vendor_qs_json'] = json.dumps([])
                context['vendor_purchases_json'] = json.dumps(purchases_list)
                context['vendor_reviews_json'] = json.dumps([])
                context['target_vendor'] = target_vendor

        elif 'users' in path and 'vendors' not in path:
            users_qs = User.objects.filter(role='USER')
            if admin_state:
                job_uids = Job.objects.filter(Q(location__state__iexact=admin_state) | Q(address__icontains=admin_state)).values_list('user_id', flat=True)
                qs_uids = QuickService.objects.filter(Q(location__state__iexact=admin_state) | Q(locality__icontains=admin_state)).values_list('vendor_id', flat=True)
                users_qs = users_qs.filter(Q(id__in=set(job_uids).union(set(qs_uids))) | Q(assigned_state__iexact=admin_state))

            users_data = []
            for u in users_qs:
                try:
                    profile = u.user_profile
                    mobile = profile.phone_number or '—'
                except Exception:
                    mobile = '—'
                    
                quick_services_count = ServiceBooking.objects.filter(customer=u).count()
                jobs_count = Job.objects.filter(user=u).count()
                completed_jobs = Job.objects.filter(user=u, status='completed').count()
                
                users_data.append({
                    'id': f'USR-{u.id:04d}',
                    'name': u.get_full_name() or u.username,
                    'email': u.email or '—',
                    'mobile': mobile,
                    'location': u.assigned_state or (admin_state or 'Unknown'),
                    'quickServices': quick_services_count,
                    'jobs': jobs_count,
                    'completedJobs': completed_jobs,
                    'status': 'active' if u.is_active else 'suspended',
                    'registered': u.date_joined.strftime('%Y-%m-%d') if u.date_joined else 'Unknown'
                })
            context['users_json'] = json.dumps(users_data)
            context['customers'] = users_qs.select_related('user_profile').order_by('-date_joined')
            
        elif 'vendors' in path:
            vendors = VendorProfile.objects.select_related('user').all()
            if admin_state:
                vendors = vendors.filter(Q(location__icontains=admin_state) | Q(user__assigned_state__iexact=admin_state))

            if 'company-vendors' in path:
                vendors = vendors.filter(vendor_type='company')

            vendors_data = []
            for profile in vendors:
                user = profile.user
                v_type = profile.vendor_type
                total_bids = Bid.objects.filter(vendor=user).count()
                completed_jobs = Job.objects.filter(bids__vendor=user, status='completed').distinct().count()
                
                contact_phone = '—'
                try:
                    if hasattr(user, 'user_profile') and user.user_profile.phone_number:
                        contact_phone = user.user_profile.phone_number
                except Exception:
                    pass

                vendors_data.append({
                    'id': f'VEN-{user.id:04d}',
                    'name': profile.company_name or user.get_full_name() or user.username,
                    'email': user.email or '—',
                    'type': v_type,
                    'contact': contact_phone,
                    'category': profile.category or 'Uncategorized',
                    'location': profile.location or (admin_state or 'Unknown'),
                    'totalBids': total_bids,
                    'completedJobs': completed_jobs,
                    'bidCredits': getattr(profile, 'bid_credits', 100), 
                    'status': 'active' if user.is_active else 'suspended',
                    'registered': profile.registered_date.strftime('%Y-%m-%d') if profile.registered_date else 'Unknown'
                })
            context['vendors_json'] = json.dumps(vendors_data)
            
    if path == 'jobs/details':
        job_id_raw = request.GET.get('id')
        if job_id_raw:
            try:
                # e.g., 'JOB-0001' -> 1
                job_id = int(job_id_raw.replace('JOB-', '')) if isinstance(job_id_raw, str) and job_id_raw.startswith('JOB-') else int(job_id_raw)
                job_obj = Job.objects.select_related('user', 'category', 'location').get(id=job_id)

                # Strict territory check for Area Admin
                admin_state, is_area_admin, available_states, co_admins = get_admin_state_context(request)
                if is_area_admin and admin_state:
                    job_in_state = (job_obj.location and job_obj.location.state and job_obj.location.state.lower() == admin_state.lower()) or (admin_state.lower() in (job_obj.address or '').lower()) or (bool(job_obj.user.assigned_state and job_obj.user.assigned_state.lower() == admin_state.lower()))
                    if not job_in_state:
                        messages.error(request, f"Access Denied: Job is outside your assigned territory ({admin_state}).")
                        return redirect('/jobs/index.html')

                context['job'] = job_obj
                
                try:
                    u_profile = job_obj.user.user_profile
                    mobile = u_profile.phone_number or '—'
                except Exception:
                    mobile = '—'
                context['job_customer_mobile'] = mobile
                
                # Also fetch bids / vendor requests for this service
                bids = Bid.objects.filter(job=job_obj).select_related('vendor', 'vendor__vendor_profile')
                context['vendor_requests'] = bids
                
                selected_vendor_name = None
                for b in bids:
                    if b.status == 'selected':
                        try:
                            selected_vendor_name = b.vendor.vendor_profile.company_name or b.vendor.get_full_name() or b.vendor.username
                        except Exception:
                            selected_vendor_name = b.vendor.get_full_name() or b.vendor.username
                        break
                context['selected_vendor_name'] = selected_vendor_name
            except (ValueError, Job.DoesNotExist):
                pass

    elif path == 'quick-services/details':
        qs_id_raw = request.GET.get('id')
        if qs_id_raw:
            try:
                # e.g., 'QS-0001' -> 1
                qs_id = int(qs_id_raw.replace('QS-', '')) if isinstance(qs_id_raw, str) and qs_id_raw.startswith('QS-') else int(qs_id_raw)
                service = QuickService.objects.select_related('vendor', 'category', 'location').get(id=qs_id)

                # Strict territory check for Area Admin
                admin_state, is_area_admin, available_states, co_admins = get_admin_state_context(request)
                if is_area_admin and admin_state:
                    if not is_service_in_state(service, admin_state):
                        messages.error(request, f"Access Denied: Quick Service is outside your assigned territory ({admin_state}).")
                        return redirect('/quick-services/index.html')

                context['service'] = service
                context['admin_state'] = admin_state
                context['is_area_admin'] = is_area_admin
                
                try:
                    u_profile = service.user.user_profile
                    mobile = u_profile.phone_number or '—'
                except Exception:
                    mobile = '—'
                context['service_customer_mobile'] = mobile
                
                # Also fetch bids / vendor requests for this service
                bids = Bid.objects.filter(quick_service=service).select_related('vendor', 'vendor__vendor_profile')
                context['vendor_requests'] = bids
                
                selected_vendor_name = None
                for b in bids:
                    if b.status == 'selected':
                        try:
                            selected_vendor_name = b.vendor.vendor_profile.company_name or b.vendor.get_full_name() or b.vendor.username
                        except Exception:
                            selected_vendor_name = b.vendor.get_full_name() or b.vendor.username
                        break
                context['selected_vendor_name'] = selected_vendor_name
            except (ValueError, QuickService.DoesNotExist):
                pass

    elif (('admin' in path and 'quick-services' in path) or path in ['quick-services', 'quick-services/index']):
        from django.db.models import Count, Prefetch
        admin_state, is_area_admin, available_states, co_admins = get_admin_state_context(request)
        context['admin_state'] = admin_state
        context['is_area_admin'] = is_area_admin
        quick_services = QuickService.objects.exclude(category__service_type='job').select_related('vendor', 'category', 'location').annotate(vendor_requests_count=Count('legacy_bids')).prefetch_related(Prefetch('legacy_bids', queryset=Bid.objects.filter(status='selected').select_related('vendor', 'vendor__vendor_profile'), to_attr='selected_bids')).order_by('-created_at')
        if admin_state:
            quick_services = quick_services.filter(get_in_state_qs_filter(admin_state))
        
        category_ids = quick_services.values_list('category_id', flat=True).distinct()
        from myapp.models import Category
        context['qs_categories'] = Category.objects.filter(id__in=category_ids).order_by('name')

        qs_data = []
        for qs in quick_services:
            u = qs.user
            try:
                u_profile = u.user_profile
                mobile = u_profile.phone_number or '—'
            except Exception:
                mobile = '—'
            
            selected_vendor_name = '—'
            if hasattr(qs, 'selected_bids') and qs.selected_bids:
                selected_bid = qs.selected_bids[0]
                try:
                    selected_vendor_name = selected_bid.vendor.vendor_profile.company_name or selected_bid.vendor.get_full_name() or selected_bid.vendor.username
                except Exception:
                    selected_vendor_name = selected_bid.vendor.get_full_name() or selected_bid.vendor.username

            qs_data.append({
                'id': f'QS-{qs.id:04d}',
                'raw_id': qs.id,
                'customer': u.get_full_name() or u.username,
                'customerMobile': mobile,
                'customerId': f'USR-{u.id:04d}',
                'avatar_class': f'av-{(u.id % 5) + 1}',
                'title': qs.title,
                'category': qs.category.name if getattr(qs, 'category', None) else 'Uncategorized',
                'location': f"{qs.location.city}, {qs.location.state}" if getattr(qs, 'location', None) else (admin_state or 'Unknown'),
                'locality': qs.locality or '',
                'budget': float(qs.base_price) if getattr(qs, 'base_price', None) else 0,
                'vendorRequests': getattr(qs, 'vendor_requests_count', 0),
                'selectedVendor': selected_vendor_name,
                'status': qs.status,
                'created': qs.created_at.strftime('%Y-%m-%d') if qs.created_at else 'Unknown'
            })
        context['quick_services_json'] = json.dumps(qs_data)
        context['quick_services_list'] = qs_data
        
        closed_statuses = {'completed', 'cancelled', 'closed', 'paused', 'inactive'}
        context['active_qs'] = [qs for qs in qs_data if qs['status'] not in closed_statuses]
        context['closed_qs'] = [qs for qs in qs_data if qs['status'] in closed_statuses]
        
        req_status = request.GET.get('status', '').strip().lower()
        context['initial_tab'] = 'closed' if req_status in closed_statuses else 'active'
        
        
    elif 'jobs' in path:
        from django.db.models import Count, Prefetch
        admin_state, is_area_admin, available_states, co_admins = get_admin_state_context(request)
        context['admin_state'] = admin_state
        context['is_area_admin'] = is_area_admin
        jobs = Job.objects.select_related('user', 'category', 'location').annotate(vendor_requests_count=Count('bids')).prefetch_related(Prefetch('bids', queryset=Bid.objects.filter(status='selected').select_related('vendor', 'vendor__vendor_profile'), to_attr='selected_bids')).order_by('-created_at')
        if admin_state:
            jobs = jobs.filter(Q(location__state__iexact=admin_state) | Q(address__icontains=admin_state))
        jobs_data = []
        for job in jobs:
            u = job.user
            try:
                u_profile = u.user_profile
                mobile = u_profile.phone_number or '—'
            except Exception:
                mobile = '—'
            
            selected_vendor_name = '—'
            if hasattr(job, 'selected_bids') and job.selected_bids:
                selected_bid = job.selected_bids[0]
                try:
                    selected_vendor_name = selected_bid.vendor.vendor_profile.company_name or selected_bid.vendor.get_full_name() or selected_bid.vendor.username
                except Exception:
                    selected_vendor_name = selected_bid.vendor.get_full_name() or selected_bid.vendor.username

            jobs_data.append({
                'id': f'JOB-{job.id:04d}',
                'customer': u.get_full_name() or u.username,
                'customerMobile': mobile,
                'customerId': f'USR-{u.id:04d}',
                'avatar_class': f'av-{(u.id % 5) + 1}',
                'title': job.title,
                'category': job.category.name if getattr(job, 'category', None) else 'Uncategorized',
                'location': f"{job.location.city}, {job.location.state}" if getattr(job, 'location', None) else (admin_state or 'Unknown'),
                'budget': float(job.budget) if job.budget else 0,
                'vendorRequests': getattr(job, 'vendor_requests_count', 0),
                'selectedVendor': selected_vendor_name,
                'status': job.status,
                'created': job.created_at.strftime('%Y-%m-%d') if job.created_at else 'Unknown'
            })
        
        active_statuses = {'open', 'active', 'progress', 'selected'}
        closed_statuses = {'completed', 'cancelled', 'closed'}
        context['active_jobs'] = [j for j in jobs_data if j['status'] in active_statuses]
        context['closed_jobs'] = [j for j in jobs_data if j['status'] in closed_statuses]
        
    if 'vendor/profile' in path:
        u = request.user
        try:
            vendor_profile = u.vendor_profile
        except Exception:
            vendor_profile = None
            
        if request.method == 'POST' and 'edit' in path:
            save_vendor_profile_changes(request, u)
            messages.success(request, "Vendor profile updated successfully!")
            return redirect('/vendor/profile/index.html')
            
        # Context for rendering profile
        context['vendor_profile'] = vendor_profile
        context['user_profile'] = getattr(u, 'user_profile', None)
        
        # Vendor stats
        context['total_bids_count'] = Bid.objects.filter(vendor=u).count()
        context['selected_bids_count'] = Bid.objects.filter(vendor=u, status='selected').count()
        context['completed_jobs_count'] = Bid.objects.filter(vendor=u, status='completed').count()

    elif 'profile' in path: # for user or admin profile
        u = request.user
        admin_state, is_area_admin, available_states, co_admins = get_admin_state_context(request)
        if getattr(u, 'role', '') == 'ADMIN' or u.is_superuser:
            context['admin_name'] = u.get_full_name() or u.username
            context['admin_email'] = u.email
            context['admin_state'] = admin_state or "All Territories (Global Platform)"
            context['is_area_admin'] = is_area_admin
            context['role_display'] = f"Area Admin ({admin_state})" if (is_area_admin and admin_state) else ("Super Admin" if u.is_superuser else "Admin")
            try:
                context['admin_mobile'] = u.user_profile.phone_number or "Not Set"
            except Exception:
                context['admin_mobile'] = "Not Set"
            
            context['admin_last_login'] = u.last_login.strftime('%Y-%m-%d %H:%M') if u.last_login else "Never"
            
            users_qs = User.objects.exclude(is_superuser=True)
            if admin_state:
                job_uids = Job.objects.filter(Q(location__state__iexact=admin_state) | Q(address__icontains=admin_state)).values_list('user_id', flat=True)
                qs_uids = QuickService.objects.filter(Q(location__state__iexact=admin_state) | Q(locality__icontains=admin_state)).values_list('vendor_id', flat=True)
                users_qs = users_qs.filter(Q(id__in=set(job_uids).union(set(qs_uids))) | Q(assigned_state__iexact=admin_state))
            context['actUsers'] = users_qs.count()
            
            sub_qs = Subscription.objects.filter(status='success')
            if admin_state:
                sub_qs = sub_qs.filter(vendor__vendor_profile__location__icontains=admin_state)
            rev = sub_qs.aggregate(Sum('amount'))['amount__sum']
            context['actRevenue'] = rev if rev else 0
        else:
            context['qs_count'] = ServiceBooking.objects.filter(customer=u).count()
            context['jobs_count'] = Job.objects.filter(user=u).count()
            context['completed_qs'] = ServiceBooking.objects.filter(customer=u, status='completed').count()
            context['completed_jobs'] = Job.objects.filter(user=u, status='completed').count()
            context['vendors_selected'] = Bid.objects.filter(job__user=u, status='selected').count()
        
    if path == 'user/jobs/compare':
        job_id = request.GET.get('job_id')
        if job_id:
            try:
                job = Job.objects.get(id=job_id, user=request.user)
                bids = Bid.objects.filter(job=job).select_related('vendor', 'vendor__vendor_profile')
                context['job'] = job
                context['bids'] = bids
            except Job.DoesNotExist:
                pass

    if path == 'user/quick-services/compare':
        qs_id = request.GET.get('qs_id')
        if qs_id:
            try:
                qs = ServiceBooking.objects.get(id=qs_id, customer=request.user)
                bids = Bid.objects.filter(quick_service=qs).select_related('vendor', 'vendor__vendor_profile')
                context['qs'] = qs
                context['bids'] = bids
            except QuickService.DoesNotExist:
                pass

    if path == 'user/jobs/quotations' or path == 'user/quick-services/quotations':
        job_id = request.GET.get('job_id')
        if job_id:
            bids = Bid.objects.filter(job_id=job_id).select_related('vendor', 'job')
        else:
            bids = Bid.objects.all().select_related('vendor', 'job')
            
        bids_data = []
        for bid in bids:
            vendor = bid.vendor
            try:
                profile = vendor.vendor_profile
                company = profile.company_name or vendor.get_full_name() or vendor.username
                rating = float(profile.rating)
                category = profile.category or 'General Contractor'
            except Exception:
                company = vendor.get_full_name() or vendor.username
                rating = 4.5
                category = 'General Contractor'
                
            completed_jobs = Job.objects.filter(bids__vendor=vendor, status='completed').distinct().count()
            
            bids_data.append({
                'id': bid.id,
                'job_id': bid.job_id,
                'vendor_id': vendor.id,
                'price': float(bid.amount),
                'rating': rating,
                'experience': 5,
                'availability': 'available',
                'vendor_name': company,
                'vendor_initials': company[:2].upper() if company else 'V',
                'vendor_category': category,
                'completed_jobs': completed_jobs,
                'estimated_time': getattr(bid, 'estimated_time', '15 days'),
                'proposal': getattr(bid, 'proposal', 'Standard quotation terms apply.'),
                'attachment_url': bid.attachment.url if bid.attachment else None,
                'status': bid.status
            })
        context['quotations_json'] = json.dumps(bids_data)

    if path in ['user/jobs/quotation-details', 'user/quick-services/quotation-details']:
        bid_id = request.GET.get('bid_id')
        if bid_id:
            try:
                bid = Bid.objects.select_related('vendor', 'job', 'quick_service').get(id=bid_id)
                context['bid'] = bid
                
                vendor = bid.vendor
                try:
                    profile = vendor.vendor_profile
                    company = profile.company_name or vendor.get_full_name() or vendor.username
                    rating = float(profile.rating)
                    category = profile.category or 'General Contractor'
                except Exception:
                    company = vendor.get_full_name() or vendor.username
                    rating = 4.5
                    category = 'General Contractor'
                    
                context['vendor_info'] = {
                    'name': company,
                    'initials': company[:2].upper() if company else 'V',
                    'category': category,
                    'rating': rating,
                    'completed_jobs': Job.objects.filter(bids__vendor=vendor, status='completed').distinct().count()
                }
            except Bid.DoesNotExist:
                return redirect('/user/jobs/quotations.html' if 'jobs' in path else '/user/quick-services/quotations.html')
        else:
            return redirect('/user/jobs/quotations.html' if 'jobs' in path else '/user/quick-services/quotations.html')
            
    if 'messages/index' in path or 'messages/chat' in path or path in ['user/messages', 'vendor/messages']:
        u = request.user
        if not u.is_authenticated:
            return redirect('/login/')
            
        is_vendor = 'vendor' in path
        target_id = request.GET.get('vendor_id') or request.GET.get('user_id') or request.GET.get('customer_id')

        # If accessing index with a target user, redirect directly to active chat window
        if ('messages/index' in path or path in ['user/messages', 'vendor/messages']) and target_id:
            param = f'user_id={target_id}' if is_vendor else f'vendor_id={target_id}'
            chat_path = '/vendor/messages/chat.html' if is_vendor else '/user/messages/chat.html'
            return redirect(f'{chat_path}?{param}')
        
        # Determine conversations (unique opposite party)
        conversations_qs = Message.objects.filter(
            Q(sender=u) | Q(receiver=u)
        ).values('sender', 'receiver').distinct()
        
        contact_ids = set()
        for c in conversations_qs:
            if c['sender'] != u.id: contact_ids.add(c['sender'])
            if c['receiver'] != u.id: contact_ids.add(c['receiver'])
            
        if is_vendor:
            # Also include customers from bookings and bids
            booking_cust_ids = ServiceBooking.objects.filter(vendor=u, customer__isnull=False).values_list('customer_id', flat=True)
            contact_ids.update(booking_cust_ids)
            bid_cust_ids = Bid.objects.filter(vendor=u, job__user__isnull=False).values_list('job__user_id', flat=True)
            contact_ids.update(bid_cust_ids)
        else:
            # Also include vendors from bookings and bids
            booking_vendor_ids = ServiceBooking.objects.filter(customer=u, vendor__isnull=False).values_list('vendor_id', flat=True)
            contact_ids.update(booking_vendor_ids)
            bid_vendor_ids = Bid.objects.filter(job__user=u, vendor__isnull=False).values_list('vendor_id', flat=True)
            contact_ids.update(bid_vendor_ids)
            
        contacts = User.objects.filter(id__in=contact_ids).exclude(id=u.id)
            
        conversations_list = []
        for contact in contacts:
            latest_msg = Message.objects.filter(
                Q(sender=u, receiver=contact) | Q(sender=contact, receiver=u)
            ).order_by('-created_at').first()
            
            unread_count = Message.objects.filter(sender=contact, receiver=u, is_read=False).count()
            
            name = contact.get_full_name() or contact.username
            if not is_vendor:
                try:
                    if hasattr(contact, 'vendor_profile') and contact.vendor_profile:
                        name = contact.vendor_profile.company_name or name
                except Exception:
                    pass
                    
            conversations_list.append({
                'id': contact.id,
                'vendor_id': contact.id, # useful for user side
                'user_id': contact.id, # useful for vendor side
                'name': name,
                'initials': name[:2].upper() if name else 'C',
                'latest_message': latest_msg,
                'unread_count': unread_count,
            })
            
        conversations_list.sort(key=lambda x: (x['latest_message'] is not None, x['latest_message'].created_at if x['latest_message'] else None), reverse=True)
        context['conversations'] = conversations_list
        
        if 'messages/chat' in path:
            other_user_id = request.GET.get('vendor_id') or request.GET.get('user_id') or request.GET.get('customer_id')
            if not other_user_id and conversations_list:
                other_user_id = conversations_list[0]['id']
                
            if other_user_id:
                try:
                    other_user = User.objects.filter(id=other_user_id).first()
                except Exception:
                    other_user = None
                    
                if other_user:
                    # Mark messages as read
                    Message.objects.filter(sender=other_user, receiver=u, is_read=False).update(is_read=True)
                    
                    if request.method == 'POST':
                        content = request.POST.get('content', '').strip()
                        attachment = request.FILES.get('attachment')
                        if content or attachment:
                            msg = Message.objects.create(
                                sender=u,
                                receiver=other_user,
                                content=content,
                                attachment=attachment
                            )
                            
                            try:
                                from channels.layers import get_channel_layer
                                from asgiref.sync import async_to_sync
                                channel_layer = get_channel_layer()
                                user_ids = sorted([u.id, other_user.id])
                                room_group_name = f'chat_{user_ids[0]}_{user_ids[1]}'
                                
                                # Build text display for attachment if any
                                extra = f' <br><a href="{msg.attachment.url}" target="_blank">Attachment</a>' if attachment else ''
                                
                                async_to_sync(channel_layer.group_send)(
                                    room_group_name,
                                    {
                                        'type': 'chat_message',
                                        'message': (msg.content or '') + extra,
                                        'sender_id': u.id,
                                        'sender_name': u.get_full_name() or u.username,
                                        'time': msg.created_at.strftime("%I:%M %p").lstrip('0')
                                    }
                                )
                            except Exception:
                                pass
                                
                            # Redirect to prevent duplicate submission
                            param = '?vendor_id=' + str(other_user.id) if not is_vendor else '?user_id=' + str(other_user.id)
                            return redirect('/' + path + '.html' + param)
                            
                    chat_messages = Message.objects.filter(
                        Q(sender=u, receiver=other_user) | Q(sender=other_user, receiver=u)
                    ).order_by('created_at')
                    context['chat_messages'] = chat_messages
                    
                    name = other_user.get_full_name() or other_user.username
                    category = 'Service Partner' if not is_vendor else 'Customer'
                    if not is_vendor:
                        try:
                            if hasattr(other_user, 'vendor_profile') and other_user.vendor_profile:
                                name = other_user.vendor_profile.company_name or name
                                category = other_user.vendor_profile.category or 'Service Partner'
                        except Exception:
                            category = 'Vendor'
                            
                    context['chat_user'] = {
                        'id': other_user.id,
                        'name': name,
                        'initials': name[:2].upper() if name else 'U',
                        'category': category,
                    }
                    context['chat_vendor'] = context['chat_user'] # alias for templates
            
    if (path in ['user/dashboard', 'user/index', 'user', 'dashboard', 'index'] or mapped_path in ['user-dashboard/dashboard', 'user-dashboard/index']) and request.user.is_authenticated and getattr(request.user, 'role', '') in ['USER', 'CUSTOMER']:
        context.update(get_user_dashboard_context(request.user, request=request))

    if 'user/jobs/selected-vendors' in path or 'jobs/selected-vendors' in mapped_path:
        job_id = request.GET.get('job_id') or request.GET.get('id')
        if job_id:
            bids = Bid.objects.filter(job_id=job_id, status__in=['selected', 'completed']).select_related('vendor', 'vendor__vendor_profile', 'job')
        else:
            bids = Bid.objects.filter(Q(job__user=request.user) | Q(quick_service__vendor=request.user), status__in=['selected', 'completed']).select_related('vendor', 'vendor__vendor_profile', 'job', 'quick_service')
        context['selected_bids'] = bids

    if 'user/vendors' in path or 'user-dashboard/vendors' in mapped_path:
        v_id = request.GET.get('id')
        if v_id:
            try:
                v_prof = VendorProfile.objects.select_related('user').get(id=v_id)
                context['vendor_profile'] = v_prof
                context['vendor_jobs_count'] = Job.objects.filter(bids__vendor=v_prof.user, status='completed').distinct().count()
                context['vendor_reviews'] = ServiceReview.objects.filter(vendor=v_prof.user, status='published').select_related('customer', 'job', 'quick_service').order_by('-created_at')
            except VendorProfile.DoesNotExist:
                pass
        context['vendors'] = VendorProfile.objects.select_related('user').all()

    if 'vendor/jobs/selected-jobs' in path:
        if request.user.is_authenticated:
            context['selected_bids'] = Bid.objects.filter(vendor=request.user, status__in=['selected', 'completed']).select_related('job', 'quick_service', 'job__user', 'quick_service__vendor').order_by('-created_at')

    if 'vendor/jobs/bid-details' in path:
        bid_id = request.GET.get('bid_id') or request.GET.get('id')
        if bid_id and request.user.is_authenticated:
            try:
                context['bid'] = Bid.objects.select_related('job', 'job__user', 'quick_service', 'quick_service__vendor').get(id=bid_id, vendor=request.user)
            except Bid.DoesNotExist:
                pass

    if 'bid-credits' in path and request.user.is_authenticated:
        gs_obj = GlobalSettings.objects.first()
        single_bid_cost = float(gs_obj.single_bid_cost) if gs_obj and gs_obj.single_bid_cost else 20.0
        context['single_bid_cost'] = single_bid_cost

        db_plans = list(BidPlan.objects.filter(is_active=True).order_by('order', 'price'))
        BID_CREDIT_PACKAGES = {}
        for p in db_plans:
            BID_CREDIT_PACKAGES[str(p.id)] = {
                'id': str(p.id),
                'name': p.name,
                'tagline': p.tagline or f'{p.credits} Bids Pack',
                'price': float(p.price),
                'original_price': float(p.original_price) if p.original_price else None,
                'credits': p.credits,
                'cost_per_credit': p.cost_per_bid,
                'popular': p.is_popular,
                'features': [
                    f'{p.credits} Bid Credits added',
                    'Credits never expire',
                    'Use on any available Long Job',
                    'Instant activation upon payment'
                ]
            }

        if not BID_CREDIT_PACKAGES:
            BID_CREDIT_PACKAGES = {
                'starter': {'id': 'starter', 'name': 'Starter Pack', 'tagline': '5 bids for ₹100', 'price': 100, 'credits': 5, 'cost_per_credit': 20, 'popular': False, 'features': ['5 Bid Credits', 'Credits never expire', 'Use on any available Long Job', 'Instant activation']},
                'value': {'id': 'value', 'name': 'Value Pack', 'tagline': '10 bids for ₹200', 'price': 200, 'credits': 10, 'cost_per_credit': 20, 'popular': True, 'features': ['10 Bid Credits', 'Credits never expire', 'Use on any available Long Job', 'Instant activation']},
                'pro': {'id': 'pro', 'name': 'Pro Pack', 'tagline': '30 bids for ₹500', 'price': 500, 'credits': 30, 'cost_per_credit': 16.6, 'popular': False, 'features': ['30 Bid Credits', 'Credits never expire', 'Use on any available Long Job', 'Instant activation']}
            }

        context['credit_packages'] = list(BID_CREDIT_PACKAGES.values())
        vp_obj = getattr(request.user, 'vendor_profile', None)
        curr_bids = (vp_obj.available_bids if vp_obj and vp_obj.available_bids is not None else 5)
        context['available_bids'] = curr_bids
        context['available_balance'] = curr_bids
        context['remaining_credits'] = curr_bids

        # Checkout Flow
        if 'checkout' in path:
            first_pkg_key = next(iter(BID_CREDIT_PACKAGES))
            selected_pkg_id = request.GET.get('package', first_pkg_key)
            selected_pkg = BID_CREDIT_PACKAGES.get(str(selected_pkg_id)) or BID_CREDIT_PACKAGES.get(selected_pkg_id, BID_CREDIT_PACKAGES[first_pkg_key])
            context['selected_pkg'] = selected_pkg

            if request.method == 'POST':
                pkg_key = request.POST.get('package_id', selected_pkg_id)
                pkg_to_buy = BID_CREDIT_PACKAGES.get(str(pkg_key)) or BID_CREDIT_PACKAGES.get(pkg_key) or selected_pkg
                payment_method = request.POST.get('payment', 'UPI')
                upi_id = request.POST.get('upi_id', '')

                # Create Subscription Record
                sub = Subscription.objects.create(
                    vendor=request.user,
                    package_name=f"{pkg_to_buy['name']} ({pkg_to_buy['credits']} Credits)",
                    amount=pkg_to_buy['price'],
                    credits_added=pkg_to_buy['credits'],
                    status='success'
                )

                # Add Credits to Vendor Profile
                vp = getattr(request.user, 'vendor_profile', None)
                if vp:
                    curr_val = vp.available_bids if vp.available_bids is not None else 0
                    vp.available_bids = int(curr_val) + int(pkg_to_buy['credits'])
                    vp.save(update_fields=['available_bids'])
                    new_bal = vp.available_bids
                else:
                    new_bal = int(pkg_to_buy['credits'])

                # Record BidCreditTransaction
                txn = BidCreditTransaction.objects.create(
                    vendor=request.user,
                    transaction_type='purchased',
                    credits=pkg_to_buy['credits'],
                    description=f"{pkg_to_buy['name']} purchase via {payment_method}",
                    related_subscription=sub
                )

                context['payment_success'] = True
                context['txn'] = txn
                context['sub'] = sub
                context['purchased_pkg'] = pkg_to_buy
                context['new_balance'] = new_bal
                context['remaining_credits'] = new_bal
                context['available_bids'] = new_bal
                context['available_balance'] = new_bal
                messages.success(request, f"Payment successful! {pkg_to_buy['credits']} bid credits added to your account.")

        # Purchase History
        purchases = Subscription.objects.filter(vendor=request.user).order_by('-created_at')
        context['purchases'] = purchases
        context['subscriptions'] = purchases
        context['total_spent'] = purchases.filter(status='success').aggregate(Sum('amount'))['amount__sum'] or 0

        # Credit Transactions Feed & Lifetime Stats
        # Ensure default welcome credits record exists if brand new vendor
        if not BidCreditTransaction.objects.filter(vendor=request.user).exists():
            current_creds = getattr(request.user.vendor_profile, 'available_bids', 5)
            if current_creds > 0:
                BidCreditTransaction.objects.create(
                    vendor=request.user,
                    transaction_type='bonus',
                    credits=current_creds,
                    description="Welcome bonus credits on account registration"
                )

        credit_txns = BidCreditTransaction.objects.filter(vendor=request.user).select_related('related_job', 'related_subscription').order_by('-created_at')
        context['credit_transactions'] = credit_txns

        lifetime_purchased = credit_txns.filter(credits__gt=0).aggregate(Sum('credits'))['credits__sum'] or 0
        lifetime_used = abs(credit_txns.filter(credits__lt=0).aggregate(Sum('credits'))['credits__sum'] or 0)
        context['lifetime_purchased'] = lifetime_purchased
        context['lifetime_used'] = lifetime_used

    if 'payments' in path or 'subscriptions' in path:
        admin_state, is_area_admin, available_states, co_admins = get_admin_state_context(request)
        context['admin_state'] = admin_state
        context['is_area_admin'] = is_area_admin
        subscriptions = Subscription.objects.select_related('vendor', 'vendor__vendor_profile').all().order_by('-created_at')
        if admin_state:
            subscriptions = subscriptions.filter(Q(vendor__vendor_profile__location__icontains=admin_state) | Q(vendor__assigned_state__iexact=admin_state))
        purchases_data = []
        for s in subscriptions:
            v_user = s.vendor
            v_profile = getattr(v_user, 'vendor_profile', None)
            v_name = v_profile.company_name if (v_profile and v_profile.company_name) else (v_user.get_full_name() or v_user.username)
            v_type = getattr(v_profile, 'vendor_type', 'company')
            credits = 100 if '100' in s.package_name else (50 if '50' in s.package_name else (25 if '25' in s.package_name else (15 if '15' in s.package_name else 10)))
            purchases_data.append({
                'id': f'TXN-BC-{s.id:04d}',
                'vendor': v_name,
                'vendorId': f'VEN-{v_user.id:04d}',
                'vendorType': v_type,
                'package': s.package_name,
                'credits': credits,
                'amount': float(s.amount),
                'paymentStatus': s.status,
                'date': s.created_at.strftime('%Y-%m-%d %H:%M') if s.created_at else 'Unknown'
            })
        context['purchases_json'] = json.dumps(purchases_data)
        context['purchases'] = purchases_data
        context['payments'] = subscriptions
        context['subscriptions'] = subscriptions
        context['total_payments_amount'] = subscriptions.filter(status='success').aggregate(Sum('amount'))['amount__sum'] or 0
        context['total_revenue'] = context['total_payments_amount']

    if 'users/customers' in path:
        admin_state, is_area_admin, available_states, co_admins = get_admin_state_context(request)
        context['admin_state'] = admin_state
        context['is_area_admin'] = is_area_admin
        customers_qs = User.objects.filter(role='USER').select_related('user_profile')
        if admin_state:
            job_uids = Job.objects.filter(Q(location__state__iexact=admin_state) | Q(address__icontains=admin_state)).values_list('user_id', flat=True)
            qs_uids = QuickService.objects.filter(Q(location__state__iexact=admin_state) | Q(locality__icontains=admin_state)).values_list('vendor_id', flat=True)
            customers_qs = customers_qs.filter(Q(id__in=set(job_uids).union(set(qs_uids))) | Q(assigned_state__iexact=admin_state))
        context['customers'] = customers_qs.order_by('-date_joined')

    if 'users/kyc-approvals' in path:
        admin_state, is_area_admin, available_states, co_admins = get_admin_state_context(request)
        context['admin_state'] = admin_state
        context['is_area_admin'] = is_area_admin
        
        kycs_qs = VendorKYC.objects.select_related('vendor', 'vendor__vendor_profile', 'vendor__user_profile', 'reviewed_by').all()
        if admin_state:
            kycs_qs = kycs_qs.filter(get_in_state_kyc_filter(admin_state))
        
        # Calculate territory stats across all statuses
        context['total_kyc_count'] = kycs_qs.count()
        context['pending_kyc_count'] = kycs_qs.filter(status='pending').count()
        context['approved_kyc_count'] = kycs_qs.filter(status='approved').count()
        context['rejected_kyc_count'] = kycs_qs.filter(status='rejected').count()

        status_filter = request.GET.get('status', 'all').strip()
        q_search = request.GET.get('q', '').strip()

        if q_search:
            kycs_qs = kycs_qs.filter(
                Q(vendor__username__icontains=q_search) |
                Q(vendor__first_name__icontains=q_search) |
                Q(vendor__last_name__icontains=q_search) |
                Q(vendor__email__icontains=q_search) |
                Q(vendor__vendor_profile__company_name__icontains=q_search) |
                Q(id_number__icontains=q_search)
            )

        if status_filter and status_filter != 'all':
            kycs_qs = kycs_qs.filter(status=status_filter)

        context['kycs'] = kycs_qs.order_by('-submitted_at', '-id')
        context['status_filter'] = status_filter
        context['q_search'] = q_search

    if 'reports/revenue' in path:
        admin_state, is_area_admin, available_states, co_admins = get_admin_state_context(request)
        context['admin_state'] = admin_state
        context['is_area_admin'] = is_area_admin
        subscriptions = Subscription.objects.select_related('vendor', 'vendor__vendor_profile').all().order_by('-created_at')
        if admin_state:
            subscriptions = subscriptions.filter(Q(vendor__vendor_profile__location__icontains=admin_state) | Q(vendor__assigned_state__iexact=admin_state))
        total_revenue = subscriptions.filter(status='success').aggregate(Sum('amount'))['amount__sum'] or 0
        context['subscriptions'] = subscriptions
        context['total_revenue'] = total_revenue
        context['success_count'] = subscriptions.filter(status='success').count()
        context['failed_count'] = subscriptions.filter(status='failed').count()

    try:
        return render(request, template_name, context)
    except TemplateDoesNotExist:
        raise Http404(f"Template {template_name} not found")

from django.contrib.auth.decorators import login_required

@login_required(login_url='user_login')
def admin_dashboard(request):
    if request.user.is_authenticated:
        if request.user.role == 'VENDOR':
            return redirect('vendor_dashboard')
        elif request.user.role in ['USER', 'CUSTOMER']:
            return redirect('user_dashboard')

    admin_state, is_area_admin, available_states, co_admins = get_admin_state_context(request)

    user_qs = User.objects.filter(role='USER')
    vendor_qs = VendorProfile.objects.select_related('user')
    job_qs = Job.objects.select_related('user', 'category', 'location')
    qs_qs = QuickService.objects.select_related('vendor', 'category', 'location')
    bid_qs = Bid.objects.select_related('vendor', 'job', 'quick_service', 'vendor__vendor_profile')
    sub_qs = Subscription.objects.select_related('vendor', 'vendor__vendor_profile')

    if admin_state:
        job_qs = job_qs.filter(Q(location__state__iexact=admin_state) | Q(address__icontains=admin_state))
        qs_qs = qs_qs.filter(Q(location__state__iexact=admin_state) | Q(locality__icontains=admin_state))
        vendor_qs = vendor_qs.filter(Q(location__icontains=admin_state) | Q(user__assigned_state__iexact=admin_state))
        
        state_customer_ids = set(job_qs.values_list('user_id', flat=True)).union(
            set(qs_qs.values_list('vendor_id', flat=True))
        )
        user_qs = user_qs.filter(Q(id__in=state_customer_ids) | Q(assigned_state__iexact=admin_state))
        
        bid_qs = bid_qs.filter(
            Q(job__in=job_qs) | Q(quick_service__in=qs_qs) | Q(vendor__vendor_profile__in=vendor_qs)
        ).distinct()
        
        sub_qs = sub_qs.filter(vendor__vendor_profile__in=vendor_qs)

    total_users = user_qs.count()
    total_vendors = vendor_qs.count()
    active_jobs = job_qs.filter(status__in=['active', 'open', 'progress', 'selected']).count()
    active_quick_services = qs_qs.filter(status__in=['active', 'open', 'progress', 'selected']).count()
    
    revenue = sub_qs.filter(status='success').aggregate(Sum('amount'))['amount__sum'] or 0

    recent_quick_services = qs_qs.order_by('-created_at')[:5]
    recent_jobs = job_qs.order_by('-created_at')[:5]
    recent_bids = bid_qs.order_by('-created_at')[:5]
    recent_vendors = vendor_qs.order_by('-registered_date')[:5]
    recent_subscriptions = sub_qs.order_by('-created_at')[:5]

    context = {
        'admin_state': admin_state,
        'is_area_admin': is_area_admin,
        'available_states': available_states,
        'co_admins': co_admins,
        'co_admins_count': co_admins.count(),
        'total_users': total_users,
        'total_customers': total_users,
        'total_vendors': total_vendors,
        'active_jobs': active_jobs,
        'active_quick_services': active_quick_services,
        'revenue': revenue,
        'recent_quick_services': recent_quick_services,
        'recent_jobs': recent_jobs,
        'recent_bids': recent_bids,
        'recent_vendors': recent_vendors,
        'recent_subscriptions': recent_subscriptions,
    }
    return render(request, 'admin-dashboard/dashboard.html', context)

def public_browse_services(request):
    from django.db.models import Q
    categories = list(Category.objects.filter(status='active').order_by('id'))
    category_id = request.GET.get('category')
    search_query = request.GET.get('search', '').strip()
    sub_query = request.GET.get('sub', '').strip()
    
    # If no category specified, default to the first active category
    selected_category = None
    if category_id and category_id.isdigit():
        selected_category = next((c for c in categories if c.id == int(category_id)), None)
    
    if not selected_category and categories:
        selected_category = categories[0]
        category_id = str(selected_category.id)

    subcategories = list(selected_category.subcategories.filter(status='active').order_by('id')) if selected_category else []

    # Build category tree for client-side reactive switching
    categories_data = []
    for cat in categories:
        categories_data.append({
            'id': cat.id,
            'name': cat.name,
            'subcategories': [{'id': s.id, 'name': s.name} for s in cat.subcategories.filter(status='active').order_by('id')]
        })
        
    services_qs = QuickService.objects.filter(status='active').select_related('vendor', 'category').order_by('-created_at')
    
    if selected_category:
        services_qs = services_qs.filter(category_id=selected_category.id)
        
    if search_query:
        services_qs = services_qs.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query) | Q(tags__icontains=search_query))
        
    if sub_query and sub_query.lower() != 'all':
        services_qs = services_qs.filter(Q(title__icontains=sub_query) | Q(tags__icontains=sub_query) | Q(description__icontains=sub_query))

    services_list = list(services_qs)
    
    # Build enriched service payload for UI & detail drawers
    enriched_services = []
    category_name = selected_category.name if selected_category else "Home Services"
    
    # Category image mappings
    cat_images = {
        'Plumbing': [
            'https://images.unsplash.com/photo-1585704032915-c3400ca199e7?w=600&auto=format&fit=crop&q=80',
            'https://images.unsplash.com/photo-1542013936693-884638332954?w=600&auto=format&fit=crop&q=80',
            'https://images.unsplash.com/photo-1507652313519-d4e9174996dd?w=600&auto=format&fit=crop&q=80'
        ],
        'Electrical': [
            'https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=600&auto=format&fit=crop&q=80',
            'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&auto=format&fit=crop&q=80'
        ],
        'AC & Appliance': [
            'https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=600&auto=format&fit=crop&q=80',
            'https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?w=600&auto=format&fit=crop&q=80'
        ],
        'Cleaning': [
            'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=600&auto=format&fit=crop&q=80',
            'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=600&auto=format&fit=crop&q=80'
        ]
    }
    
    default_imgs = cat_images.get(category_name, [
        'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=600&auto=format&fit=crop&q=80'
    ])
    
    user_lat = request.GET.get('lat')
    user_lon = request.GET.get('lon')

    def calculate_distance(lat1, lon1, lat2, lon2):
        try:
            import math
            R = 6371.0
            dlat = math.radians(float(lat2) - float(lat1))
            dlon = math.radians(float(lon2) - float(lon1))
            a = math.sin(dlat / 2)**2 + math.cos(math.radians(float(lat1))) * math.cos(math.radians(float(lat2))) * math.sin(dlon / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return round(R * c, 1)
        except Exception:
            return None

    for idx, s in enumerate(services_list):
        orig_price = round(float(s.base_price) * 1.3)

        # Image resolution: uploaded file > custom preset URL > category default
        img_url = None
        if s.image:
            try:
                img_url = s.image.url
            except Exception:
                img_url = None
        if not img_url:
            img_url = s.image_url or default_imgs[idx % len(default_imgs)]

        packages = s.service_packages if (s.service_packages and len(s.service_packages) > 0) else [
            {'name': 'Standard Service', 'price': float(s.base_price), 'original_price': orig_price, 'desc': 'Complete service inspection & resolution'}
        ]

        # Inclusions & Exclusions resolution
        inclusions = s.inclusions if (s.inclusions and len(s.inclusions) > 0) else [
            "Complete diagnostic inspection of existing fittings & components",
            "Execution by certified, background-checked professional",
            "Post-service sanitization and thorough debris cleanup",
            "30 days Sugu protection warranty on all workmanship"
        ]
        exclusions = s.exclusions if (s.exclusions and len(s.exclusions) > 0) else [
            "Major civil masonry, pipe embedding or wall tearing excluded",
            "Spare parts / extra hardware to be purchased or charged separately"
        ]
        
        s_lat = float(s.latitude) if s.latitude else 23.3697
        s_lon = float(s.longitude) if s.longitude else 85.3346
        radius = float(s.service_radius_km or 10.0)

        dist = None
        is_within_range = True
        if user_lat and user_lon:
            dist = calculate_distance(user_lat, user_lon, s_lat, s_lon)
            if dist is not None:
                is_within_range = dist <= radius
        
        enriched_services.append({
            'id': s.id,
            'title': s.title,
            'category_id': s.category_id,
            'category_name': category_name,
            'vendor_name': s.vendor.get_full_name() or s.vendor.username,
            'vendor_id': s.vendor_id,
            'locality': s.locality or "Ranchi Central",
            'latitude': s_lat,
            'longitude': s_lon,
            'service_radius_km': radius,
            'distance_km': dist,
            'is_within_range': is_within_range,
            'base_price': float(s.base_price),
            'original_price': orig_price,
            'rating': 4.8,
            'reviews_count': '1.8K',
            'image_url': img_url,
            'description': s.description or f"Professional {category_name.lower()} service by verified experts.",
            'bullets': inclusions[:3],
            'inclusions': inclusions,
            'exclusions': exclusions,
            'packages': packages,
            'tags': s.tags or '',
            'subcat_name': s.tags or ''
        })
        
    # Map subcategory names into enriched_services
    for idx, s_item in enumerate(enriched_services):
        sub_name = s_item.get('subcat_name') or ''
        if not sub_name and subcategories:
            for sb in subcategories:
                if sb.name.lower() in s_item['title'].lower() or sb.name.lower() in (s_item.get('description') or '').lower() or sb.name.lower() in (s_item.get('tags') or '').lower():
                    sub_name = sb.name
                    break
        if not sub_name and subcategories:
            sub_name = subcategories[idx % len(subcategories)].name
        s_item['subcat_name'] = sub_name

    context = {
        'services': enriched_services,
        'categories': categories,
        'subcategories': subcategories,
        'selected_category': selected_category,
        'selected_category_id': selected_category.id if selected_category else None,
        'selected_sub': sub_query,
        'categories_data_json': json.dumps(categories_data),
        'search_query': search_query,
        'sub_query': sub_query,
        'user_lat': user_lat,
        'user_lon': user_lon,
        'services_json': json.dumps(enriched_services),
        'user': request.user
    }
    return render(request, 'browse.html', context)

    
@never_cache
def home_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'ADMIN' or user.is_superuser:
                return redirect('admin_dashboard')
            elif user.role == 'VENDOR':
                return redirect('vendor_dashboard')
            elif user.role in ['USER', 'CUSTOMER']:
                return redirect('user_dashboard')
            return redirect('home')
        else:
            error = 'Invalid username, email, phone number, or password.'

    categories = Category.objects.filter(status='active').prefetch_related('subcategories').order_by('name')
    locations = Location.objects.filter(status='active').order_by('state', 'city')
    recent_bids = Bid.objects.select_related('vendor', 'vendor__vendor_profile', 'job', 'job__location').order_by('-created_at')[:6]
    
    recent_bids_data = []
    for b in recent_bids:
        target = b.job
        city = (target.location.city if target and target.location else "Ranchi")
        c_name = target.contact_name or (target.user.get_full_name() or target.user.username) if target and target.user else "Customer"
        recent_bids_data.append({
            "customer_name": c_name,
            "city": city,
            "service": target.title if target else "Home Service",
            "price": float(b.amount),
            "created": b.created_at.strftime("%I:%M %p") if b.created_at else "Just now",
            "type": "bid"
        })
        
    from .models import ServiceBooking
    recent_bookings = ServiceBooking.objects.select_related('vendor', 'customer', 'quick_service').order_by('-created_at')[:6]
    for b in recent_bookings:
        target = b.quick_service
        city = "Ranchi"
        c_name = b.customer.get_full_name() or b.customer.username if b.customer else "Customer"
        recent_bids_data.append({
            "customer_name": c_name,
            "city": city,
            "service": target.title if target else "Home Service",
            "price": float(b.total_amount),
            "created": b.created_at.strftime("%I:%M %p") if b.created_at else "Just now",
            "type": "booking"
        })
    
    # Sort combined activity by created time (simulated via order, or just let them be mixed)

    branding = SiteBranding.objects.first()
    hero = HeroSection.objects.first()
    cms_quick_services = QuickServiceCard.objects.filter(is_active=True).order_by('order', '-created_at')
    cms_featured_projects = FeaturedProjectCard.objects.filter(is_active=True).order_by('order', '-created_at')
    cms_packages = PackageCard.objects.filter(is_active=True).order_by('order', '-created_at')
    cms_testimonials = Testimonial.objects.filter(is_active=True).order_by('order', '-created_at')
    cms_trust_metrics = TrustMetric.objects.filter(is_active=True).order_by('order')

    user_city = None
    user_state = None
    is_service_available = True
    if request.user.is_authenticated:
        u_prof = getattr(request.user, 'user_profile', None)
        if u_prof and u_prof.city:
            user_city = u_prof.city.strip()
            user_state = u_prof.state.strip() if u_prof.state else None
        if not user_city:
            user_city = request.session.get('user_city') or request.COOKIES.get('sugu_user_city')
            user_state = request.session.get('user_state') or request.COOKIES.get('sugu_user_state')
        if not user_city and getattr(request.user, 'assigned_city', None):
            user_city = request.user.assigned_city.strip()
            user_state = request.user.assigned_state.strip() if request.user.assigned_state else None
        if not user_city and hasattr(request.user, 'vendor_profile') and request.user.vendor_profile and request.user.vendor_profile.location:
            parts = request.user.vendor_profile.location.split(',')
            user_city = parts[0].strip()
            if len(parts) > 1:
                user_state = parts[1].strip()

        if user_city:
            active_cities_set = {c.lower().strip() for c in locations.values_list('city', flat=True) if c}
            is_service_available = user_city.lower().strip() in active_cities_set

    context = {
        'error': error,
        'branding': branding,
        'hero': hero,
        'cms_quick_services': cms_quick_services,
        'cms_featured_projects': cms_featured_projects,
        'cms_packages': cms_packages,
        'cms_testimonials': cms_testimonials,
        'cms_trust_metrics': cms_trust_metrics,
        'categories': categories,
        'landing_services': QuickService.objects.filter(status='active').select_related('vendor', 'category').order_by('-created_at'),
        'top_services': QuickService.objects.filter(status='active').select_related('vendor', 'category').order_by('-created_at')[:8],
        'locations': locations,
        'recent_bids': recent_bids,
        'categories_json': json.dumps(list(categories.values("id", "name", "service_type", "status"))),
        'locations_json': json.dumps(list(locations.values("id", "state", "city"))),
        'recent_bids_json': json.dumps(recent_bids_data),
        'now': timezone.now(),
        'user': request.user,
        'user_city': user_city,
        'user_state': user_state,
        'is_service_available': is_service_available,
        'service_not_available': not is_service_available if user_city else False,
        'service_unavailable_city': user_city,
    }
    return render(request, 'index.html', context)

def user_login_view(request):
    next_url = request.POST.get('next') or request.GET.get('next')
    # Validate next_url to ensure it is a safe local relative path
    if next_url and (not next_url.startswith('/') or next_url.startswith('//')):
        next_url = None

    if request.user.is_authenticated:
        if next_url:
            return redirect(next_url)
        if request.user.role == 'ADMIN' or request.user.is_superuser:
            return redirect('admin_dashboard')
        elif request.user.role == 'VENDOR':
            return redirect('vendor_dashboard')
        elif request.user.role in ['USER', 'CUSTOMER']:
            return redirect('user_dashboard')
        return redirect('admin_dashboard')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.role == 'VENDOR':
                from .models import VendorKYC
                try:
                    kyc = VendorKYC.objects.get(vendor=user)
                    if kyc.status != 'approved':
                        error = f"Your profile is under verification by admins. Current status: {kyc.get_status_display()}. You can login once verified."
                        return render(request, 'login.html', {'error': error, 'next': next_url})
                except VendorKYC.DoesNotExist:
                    error = "KYC verification pending. Please complete your registration."
                    return render(request, 'login.html', {'error': error, 'next': next_url})

            login(request, user)
            if next_url:
                return redirect(next_url)
            if user.role == 'ADMIN' or user.is_superuser:
                return redirect('admin_dashboard')
            elif user.role == 'VENDOR':
                return redirect('vendor_dashboard')
            elif user.role in ['USER', 'CUSTOMER']:
                return redirect('user_dashboard')
            return redirect('admin_dashboard')
        else:
            error = 'Invalid username, email, phone number, or password.'
    return render(request, 'login.html', {'error': error, 'next': next_url})

def user_logout_view(request):
    logout(request)
    return redirect('home')

def register_user_view(request):
    error = None
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        if password != confirm_password:
            error = 'Passwords do not match.'
        elif User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            error = 'Email is already registered.'
        else:
            username = email if email else name.replace(" ", "").lower() + str(User.objects.count())
            user = User.objects.create_user(username=username, email=email, password=password, first_name=name)
            user.role = 'USER'
            user.save()
            profile_img = request.FILES.get('profile_image')
            UserProfile.objects.create(user=user, phone_number=mobile, profile_image=profile_img)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('user_dashboard')
    
    return render(request, 'register_user.html', {'error': error})

def register_vendor_view(request):
    error = None
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        company_name = request.POST.get('company_name', '').strip()
        email = request.POST.get('email', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        
        # Multi-select categories support
        categories_selected = request.POST.getlist('categories')
        if not categories_selected:
            categories_selected = request.POST.getlist('category')
        if not categories_selected and request.POST.get('category'):
            categories_selected = [c.strip() for c in request.POST.get('category').split(',') if c.strip()]
        clean_cats = [c.strip() for c in categories_selected if c.strip()]
        category = ", ".join(clean_cats) if clean_cats else ""

        state = request.POST.get('state', '').strip()
        city = request.POST.get('city', '').strip()
        location = f"{city}, {state}" if state and city else request.POST.get('location', '').strip()
        
        # New Personal Details
        dob = request.POST.get('dob') or None
        gender = request.POST.get('gender', '').strip()
        address = request.POST.get('address', '').strip()
        experience = request.POST.get('experience', 0)
        try:
            experience = int(experience)
        except ValueError:
            experience = 0
        id_proof = request.POST.get('id_proof', '').strip()
        
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        if not clean_cats:
            error = 'Please select at least one main service category.'
        elif password != confirm_password:
            error = 'Passwords do not match.'
        elif User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            error = 'Email is already registered.'
        else:
            username = email if email else name.replace(" ", "").lower() + str(User.objects.count())
            user = User.objects.create_user(username=username, email=email, password=password, first_name=name)
            user.role = 'VENDOR'
            user.save()
            
            profile_img = request.FILES.get('profile_image')
            VendorProfile.objects.create(
                user=user,
                company_name=company_name,
                category=category or "General",
                location=location,
                dob=dob,
                gender=gender,
                address=address,
                experience=experience,
                id_proof=id_proof,
                profile_image=profile_img
            )
            # You could also create UserProfile to store the mobile number if desired
            UserProfile.objects.create(user=user, phone_number=mobile, profile_image=profile_img)
            
            # Handle KYC Documents
            id_type = request.POST.get('id_type')
            id_document_front = request.FILES.get('id_document_front')
            id_document_back = request.FILES.get('id_document_back')
            business_license = request.FILES.get('business_license')
            
            if id_type and id_document_front:
                from .models import VendorKYC
                VendorKYC.objects.create(
                    vendor=user,
                    id_type=id_type,
                    id_number=id_proof or '',
                    id_document_front=id_document_front,
                    id_document_back=id_document_back,
                    business_license=business_license,
                    status='pending'
                )
            
            from django.contrib import messages
            messages.success(request, f"Vendor '{name}' registered successfully. Your profile is under verification by admins. You can login once verified.")
            return redirect('login')

    active_locations = Location.objects.filter(status='active').order_by('state', 'city')
    locations_dict = {}
    for loc in active_locations:
        if loc.state not in locations_dict:
            locations_dict[loc.state] = []
        locations_dict[loc.state].append(loc.city)

    selected_categories = request.POST.getlist('categories') or request.POST.getlist('category')
    if not selected_categories and request.POST.get('category'):
        selected_categories = [c.strip() for c in request.POST.get('category').split(',') if c.strip()]

    context = {
        'error': error,
        'categories': Category.objects.filter(status='active').order_by('name'),
        'locations_json': json.dumps(locations_dict),
        'states': sorted(locations_dict.keys()),
        'selected_categories': selected_categories,
        'selected_categories_json': json.dumps(selected_categories),
    }
    return render(request, 'register_vendor.html', context)

from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.http import require_POST

@require_POST
def create_company_vendor_view(request):
    try:
        company_name = request.POST.get('company_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        category = request.POST.get('category', '').strip()
        location = request.POST.get('location', '').strip()
        employee_code = request.POST.get('employee_code', '').strip()
        employee_details = request.POST.get('employee_details', '').strip()
        
        if User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            messages.error(request, 'Email or Username already exists.')
            return redirect('/admin-dashboard/users/company-vendors.html')
            
        username = email if email else company_name.replace(" ", "").lower() + str(User.objects.count())
        
        user = User.objects.create_user(username=username, email=email, password=password, first_name=company_name)
        user.role = 'VENDOR'
        
        # Tag with Area Admin's assigned state if created by an area admin
        if request.user.is_authenticated and request.user.role == 'ADMIN' and not request.user.is_superuser:
            user.assigned_state = request.user.assigned_state
            if request.user.assigned_state and request.user.assigned_state.lower() not in location.lower():
                location = f"{location}, {request.user.assigned_state}" if location else request.user.assigned_state
        user.save()
        
        VendorProfile.objects.create(
            user=user,
            vendor_type='company',
            company_name=company_name,
            category=category,
            location=location,
            employee_code=employee_code,
            employee_details=employee_details
        )
        
        from .models import VendorKYC
        from django.utils import timezone
        VendorKYC.objects.create(
            vendor=user,
            id_type='aadhaar',
            id_number='Admin Created',
            status='approved',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        
        messages.success(request, 'Company Vendor created successfully.')
    except Exception as e:
        messages.error(request, f'Error creating company vendor: {str(e)}')
        
    return redirect('/admin-dashboard/users/company-vendors.html')

from datetime import datetime
from django.contrib.auth.decorators import login_required

@login_required
def vendor_dashboard(request):
    user = request.user
    vendor_profile = getattr(user, 'vendor_profile', None)
    
    context = {}
    if vendor_profile:
        name = vendor_profile.company_name or user.get_full_name() or user.username
        initials = name[:2].upper() if name else "VN"
        date_str = datetime.now().strftime("%A, %d %B %Y")
        location = vendor_profile.location or "Unknown Location"
        v_type = "Company Vendor" if vendor_profile.company_name else "Individual Vendor"
        
        context.update({
            'vendor_name': name,
            'vendor_initials': initials,
            'current_date': date_str,
            'vendor_location': location,
            'vendor_type': v_type,
            'profile_image_url': vendor_profile.profile_image.url if vendor_profile.profile_image else None,
        })
    else:
        name = user.get_full_name() or user.username
        context.update({
            'vendor_name': name,
            'vendor_initials': name[:2].upper() if name else "VN",
            'current_date': datetime.now().strftime("%A, %d %B %Y"),
            'vendor_location': "Unknown Location",
            'vendor_type': "Vendor",
            'profile_image_url': None,
        })

    # Calculate dynamic stats
    from .wallet_services import get_or_create_wallet
    from django.db.models import Sum

    wallet = get_or_create_wallet(user)
    kyc = VendorKYC.objects.filter(vendor=user).first()
    pending_payouts_sum = PayoutRequest.objects.filter(vendor=user, status='pending').aggregate(total=Sum('amount'))['total'] or 0

    vendor_city = None
    vendor_categories = []
    if vendor_profile:
        if vendor_profile.location and vendor_profile.location.strip():
            vendor_city = vendor_profile.location.strip().split(',')[0].strip()
        elif getattr(vendor_profile, 'address', None):
            vendor_city = vendor_profile.address.strip().split(',')[0].strip()
        if vendor_profile.category and vendor_profile.category.strip():
            vendor_categories = vendor_profile.categories_list

    jobs_base = Job.objects.filter(status='open')
    if vendor_city:
        city_filter = (
            Q(location__city__iexact=vendor_city) |
            Q(city__iexact=vendor_city) |
            (Q(location__isnull=True) & (Q(address__icontains=vendor_city) | Q(locality__icontains=vendor_city)))
        )
        jobs_base = jobs_base.filter(city_filter)

    if vendor_categories:
        cat_filter = Q()
        has_general = any(c.lower() in ['other', 'general', 'other / general services', 'general services'] for c in vendor_categories)
        if has_general:
            cat_filter |= Q(category__isnull=True) | Q(category__name__icontains='General') | Q(category__name__icontains='Other')
        for cat_name in vendor_categories:
            if cat_name.lower() not in ['other', 'general', 'other / general services', 'general services']:
                cat_filter |= (
                    Q(category__name__iexact=cat_name) |
                    Q(category__name__icontains=cat_name) |
                    (Q(category__isnull=True) & Q(title__icontains=cat_name))
                )
        jobs_base = jobs_base.filter(cat_filter)

    # Quick services strictly under 10km
    v_lat, v_lon = resolve_coordinates_for_location(vendor_city or (vendor_profile.location if vendor_profile else ''))
    all_active_qs = QuickService.objects.filter(status__in=['active', 'open']).select_related('category', 'location', 'vendor')
    nearby_qs = []
    for qs in all_active_qs:
        q_lat = float(qs.latitude) if qs.latitude else None
        q_lon = float(qs.longitude) if qs.longitude else None
        if q_lat is None or q_lon is None:
            loc_name = (qs.locality or '') + ' ' + (qs.location.city if qs.location else '')
            q_lat, q_lon = resolve_coordinates_for_location(loc_name, default_coords=(None, None))
        if q_lat is not None and q_lon is not None:
            d = haversine_distance_km(v_lat, v_lon, q_lat, q_lon)
            if d is not None and d <= 10.0:
                qs.distance_km = d
                qs.budget = float(qs.base_price)
                nearby_qs.append(qs)

    nearby_qs.sort(key=lambda x: getattr(x, 'distance_km', 999.0))
    available_qs = len(nearby_qs)
    available_jobs = jobs_base.count()
    
    # Active bids for this vendor
    active_bids_count = Bid.objects.filter(vendor=user).exclude(status__in=['rejected', 'completed']).count()
    # Selected bids
    selected_bids_count = Bid.objects.filter(vendor=user, status='selected').count()
    # Completed bids
    completed_bids_count = Bid.objects.filter(vendor=user, status='completed').count()
    
    # Total earnings from completed bids
    earnings = Bid.objects.filter(vendor=user, status='completed').aggregate(total=Sum('amount'))['total']
    
    # Active Requests: For quick services, it could be QS where vendor bid is pending
    active_requests_count = Bid.objects.filter(vendor=user, quick_service__isnull=False, status='pending').count()
    
    my_services_count = QuickService.objects.filter(vendor=user).count()

    context.update({
        'my_services_count': my_services_count,
        'available_qs': available_qs,
        'available_jobs': available_jobs,
        'remaining_credits': getattr(vendor_profile, 'bid_credits', 5) if vendor_profile else 5,
        'active_requests': active_requests_count,
        'active_bids': active_bids_count,
        'selected_jobs': selected_bids_count,
        'completed_work': completed_bids_count,
        'total_earnings': float(earnings) if earnings else 0.0,
        'wallet': wallet,
        'wallet_balance': f"{wallet.available_balance:.2f}",
        'total_earned': wallet.total_earned,
        'total_withdrawn': wallet.total_withdrawn,
        'pending_payouts_sum': pending_payouts_sum,
        'kyc': kyc,
        'is_kyc_verified': True,
        'recent_transactions': wallet.transactions.all().order_by('-created_at')[:4],
    })

    # Fetch recent items
    context['recent_quick_services'] = nearby_qs[:3]
    context['recent_jobs'] = jobs_base.order_by('-created_at')[:4]

    return render(request, 'infinity-vendor-dashboard/dashboard.html', context)

from django.contrib.auth.decorators import login_required

@login_required
def user_dashboard(request):
    if request.method == 'POST' and request.POST.get('action') == 'complete_and_settle':
        from .wallet_services import settle_job_completion
        job_id = request.POST.get('job_id')
        qs_id = request.POST.get('quick_service_id')
        if job_id:
            try:
                j_obj = Job.objects.get(id=job_id)
                if request.user == j_obj.user or request.user.role == 'ADMIN' or request.user == j_obj.assigned_vendor:
                    settle_job_completion(job=j_obj)
                    j_obj.status = 'completed'
                    j_obj.save()
                    Bid.objects.filter(job=j_obj, status='selected').update(status='completed')
            except Job.DoesNotExist:
                pass
        elif qs_id:
            try:
                qs_obj = QuickService.objects.get(id=qs_id)
                if request.user == qs_obj.user or request.user.role == 'ADMIN':
                    settle_job_completion(quick_service=qs_obj)
                    qs_obj.status = 'completed'
                    qs_obj.save()
                    Bid.objects.filter(quick_service=qs_obj, status='selected').update(status='completed')
            except QuickService.DoesNotExist:
                pass
        return redirect('/user/dashboard')

    if request.method == 'POST' and request.POST.get('action') == 'accept_vendor':
        bid_id = request.POST.get('bid_id')
        if bid_id:
            try:
                b_obj = Bid.objects.get(id=bid_id)
                b_obj.status = 'selected'
                b_obj.save()
                if b_obj.quick_service:
                    b_obj.quick_service.status = 'selected'
                    b_obj.quick_service.save()
                if b_obj.job:
                    b_obj.job.assigned_vendor = b_obj.vendor
                    b_obj.job.status = 'selected'
                    b_obj.job.save()
            except Bid.DoesNotExist:
                pass
        return redirect('/user/dashboard')

    context = get_user_dashboard_context(request.user, request=request)
    return render(request, 'user-dashboard/dashboard.html', context)

# Re-export APIs from Api_views module
from .Api_views import (
    unified_login_api,
    unified_otp_login_api,
    check_phone_api,
    user_signup_api,
    user_login_api,
    vendor_signup_api,
    vendor_login_api,
    send_otp_api,
    verify_otp_api,
    user_otp_signup_api,
    user_otp_login_api,
    vendor_otp_signup_api,
    vendor_otp_login_api,
    add_user_api,
    user_nav_data_api,
    add_category_api,
    update_category_api,
    delete_category_api,
)

@login_required
def manage_location_view(request):
    if request.user.role != 'ADMIN' and not request.user.is_superuser:
        return HttpResponseForbidden("Access Denied")

    is_area_admin = (request.user.role == 'ADMIN' and not request.user.is_superuser)
    admin_state = request.user.assigned_state

    if request.method == 'POST':
        action = request.POST.get('action')
        loc_id = request.POST.get('id')
        
        if action == 'delete':
            if loc_id:
                loc = Location.objects.filter(id=loc_id).first()
                if loc:
                    if is_area_admin and admin_state and loc.state.lower() != admin_state.lower():
                        messages.error(request, f"Permission Denied: You can only delete cities in your assigned state ({admin_state}).")
                        return redirect('/master/locations')
                    city_deleted = loc.city
                    loc.delete()
                    messages.success(request, f"City '{city_deleted}' deleted.")
        else:
            if is_area_admin:
                # Force state strictly to assigned_state. Area Admin cannot create states or add cities in other states!
                state = admin_state
            else:
                state = request.POST.get('state_new', '').strip() or request.POST.get('state', '').strip()

            city = request.POST.get('city', '').strip()
            status = request.POST.get('status', 'active')
            
            if not state:
                messages.error(request, "State is required.")
                return redirect('/master/locations')

            if not city:
                messages.error(request, "City name is required.")
                return redirect('/master/locations')

            if loc_id:
                loc = Location.objects.filter(id=loc_id).first()
                if loc:
                    if is_area_admin and admin_state and loc.state.lower() != admin_state.lower():
                        messages.error(request, f"Permission Denied: You cannot modify locations outside your assigned state ({admin_state}).")
                        return redirect('/master/locations')
                    loc.city = city
                    loc.state = state
                    loc.status = status
                    loc.save()
                    messages.success(request, f"City '{city}' updated.")
            else:
                Location.objects.create(state=state, city=city, status=status)
                messages.success(request, f"City '{city}' added to {state}.")
        
        return redirect('/master/locations')
    return redirect('/master/locations')


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden

@login_required
def approve_kyc_view(request, kyc_id):
    if request.method == 'POST':
        if request.user.role != 'ADMIN' and not request.user.is_superuser:
            return HttpResponseForbidden("Access Denied")
        from .models import VendorKYC
        kyc = get_object_or_404(VendorKYC, id=kyc_id)
        
        # Territory authorization check: Area Admin can only approve vendors present in their state
        if request.user.role == 'ADMIN' and not request.user.is_superuser:
            admin_state = request.user.assigned_state
            if not is_vendor_in_state(kyc.vendor, admin_state):
                messages.error(request, f"Permission Denied: Vendor '{kyc.vendor.username}' does not belong to your assigned territory ({admin_state}).")
                return redirect(request.META.get('HTTP_REFERER') or '/admin-dashboard/users/kyc-approvals.html')

        kyc.status = 'approved'
        kyc.reviewed_by = request.user
        kyc.reviewed_at = timezone.now()
        kyc.save()
        vendor_name = kyc.vendor.get_full_name() or kyc.vendor.username
        messages.success(request, f"KYC verification for {vendor_name} approved successfully.")
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': f"KYC for {vendor_name} approved successfully."})
            
    return redirect(request.META.get('HTTP_REFERER') or '/admin-dashboard/users/kyc-approvals.html')

@login_required
def reject_kyc_view(request, kyc_id):
    if request.method == 'POST':
        if request.user.role != 'ADMIN' and not request.user.is_superuser:
            return HttpResponseForbidden("Access Denied")
        from .models import VendorKYC
        kyc = get_object_or_404(VendorKYC, id=kyc_id)
        
        # Territory authorization check: Area Admin can only reject vendors present in their state
        if request.user.role == 'ADMIN' and not request.user.is_superuser:
            admin_state = request.user.assigned_state
            if not is_vendor_in_state(kyc.vendor, admin_state):
                messages.error(request, f"Permission Denied: Vendor '{kyc.vendor.username}' does not belong to your assigned territory ({admin_state}).")
                return redirect(request.META.get('HTTP_REFERER') or '/admin-dashboard/users/kyc-approvals.html')

        reason = request.POST.get('admin_notes', '').strip() or "Documents did not meet platform verification criteria."
        kyc.status = 'rejected'
        kyc.reviewed_by = request.user
        kyc.admin_notes = reason
        kyc.reviewed_at = timezone.now()
        kyc.save()
        vendor_name = kyc.vendor.get_full_name() or kyc.vendor.username
        messages.warning(request, f"KYC verification for {vendor_name} has been rejected.")
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': f"KYC for {vendor_name} rejected."})

    return redirect(request.META.get('HTTP_REFERER') or '/admin-dashboard/users/kyc-approvals.html')

@login_required
def update_quick_service_status_view(request, service_id):
    if request.method != 'POST':
        return HttpResponseForbidden("Only POST method allowed.")

    if request.user.role != 'ADMIN' and not request.user.is_superuser:
        return HttpResponseForbidden("Access Denied")

    service = get_object_or_404(QuickService.objects.select_related('location', 'vendor', 'vendor__vendor_profile'), id=service_id)

    # Territory authorization check: Area Admin can only modify quick services within their assigned state
    if request.user.role == 'ADMIN' and not request.user.is_superuser:
        admin_state = request.user.assigned_state
        if not is_service_in_state(service, admin_state):
            msg = f"Permission Denied: Quick Service '{service.title}' is outside your assigned territory ({admin_state})."
            messages.error(request, msg)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': msg}, status=403)
            return redirect(request.META.get('HTTP_REFERER') or '/quick-services/index.html')

    new_status = request.POST.get('status', '').strip().lower()
    valid_statuses = {'active', 'closed', 'completed', 'cancelled', 'paused'}
    if new_status not in valid_statuses:
        msg = f"Invalid status: '{new_status}'. Allowed: {', '.join(sorted(valid_statuses))}"
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': msg}, status=400)
        messages.error(request, msg)
        return redirect(request.META.get('HTTP_REFERER') or '/quick-services/index.html')

    old_status = service.status
    service.status = new_status
    service.save(update_fields=['status'])

    action_label = "reactivated" if new_status == 'active' else "closed"
    msg = f"Quick Service 'QS-{service.id:04d}' ({service.title}) {action_label} successfully (status: {new_status.title()})."
    messages.success(request, msg)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': msg,
            'service_id': service.id,
            'old_status': old_status,
            'new_status': new_status
        })

    ref = request.META.get('HTTP_REFERER')
    if ref:
        return redirect(ref)
    target_hash = '#closed' if new_status in {'closed', 'completed', 'cancelled', 'paused'} else '#active'
    return redirect(f'/quick-services/index.html{target_hash}')

def detect_location_api(request):
    from django.http import JsonResponse
    import urllib.request, urllib.parse, json

    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    detected = None

    # If coordinates provided directly from client GPS
    if lat and lon:
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&addressdetails=1"
            req = urllib.request.Request(url, headers={'User-Agent': 'SuguLiveApp/1.0'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode())
                addr = data.get('address', {})
                poi = addr.get('amenity') or addr.get('building') or addr.get('shop') or addr.get('office')
                colony = addr.get('residential') or addr.get('suburb') or addr.get('neighbourhood') or addr.get('quarter') or addr.get('village')
                base_road = addr.get('road') or colony or ''
                road = f"{poi}, {base_road}".strip(', ') if poi and base_road else (poi or base_road or addr.get('suburb') or addr.get('neighbourhood'))
                city = addr.get('city') or addr.get('town') or addr.get('county') or addr.get('state_district') or "Ranchi"
                state = addr.get('state', 'Jharkhand')
                pincode = addr.get('postcode', '')
                
                primary = f"{road}" if road else city
                full_display = f"{primary}, {city}" if road and primary != city else f"{city}, {state}"
                
                detected = {
                    'name': full_display,
                    'primary': primary,
                    'secondary': f"{city}, {state} {pincode}".strip(),
                    'full_address': data.get('display_name', ''),
                    'city': city,
                    'state': state,
                    'lat': float(lat),
                    'lon': float(lon),
                    'source': 'live_gps'
                }
        except Exception:
            pass

    # If no coordinates or GPS reverse failed, detect via public network IP
    if not detected:
        client_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '')).split(',')[0].strip()
        ip_lat, ip_lon = None, None
        city, region = None, None

        # Try ipwho.is
        try:
            url = 'https://ipwho.is/' if client_ip.startswith(('192.168.', '10.', '172.', '127.')) else f'https://ipwho.is/{client_ip}'
            req = urllib.request.Request(url, headers={'User-Agent': 'SuguLiveApp/1.0'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode())
                if data.get('success', False):
                    city = data.get('city')
                    region = data.get('region')
                    ip_lat = data.get('latitude')
                    ip_lon = data.get('longitude')
        except Exception:
            pass

        # Secondary IP fallback
        if not ip_lat:
            try:
                url = 'http://ip-api.com/json/' if client_ip.startswith(('192.168.', '10.', '172.', '127.')) else f'http://ip-api.com/json/{client_ip}'
                req = urllib.request.Request(url, headers={'User-Agent': 'SuguLiveApp/1.0'})
                with urllib.request.urlopen(req, timeout=3) as resp:
                    data = json.loads(resp.read().decode())
                    if data.get('status') == 'success':
                        city = data.get('city')
                        region = data.get('regionName')
                        ip_lat = data.get('lat')
                        ip_lon = data.get('lon')
            except Exception:
                pass

        # If IP coordinates resolved, do reverse geocode for exact street/area
        if ip_lat and ip_lon:
            try:
                url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={ip_lat}&lon={ip_lon}"
                req = urllib.request.Request(url, headers={'User-Agent': 'SuguLiveApp/1.0'})
                with urllib.request.urlopen(req, timeout=3) as resp:
                    rdata = json.loads(resp.read().decode())
                    addr = rdata.get('address', {})
                    road = addr.get('road') or addr.get('suburb') or addr.get('neighbourhood') or addr.get('village')
                    rcity = addr.get('city') or addr.get('town') or addr.get('state_district') or city or "Ranchi"
                    rstate = addr.get('state') or region or "Jharkhand"
                    rpincode = addr.get('postcode', '')
                    
                    is_cantonment = ('cantonment' in (rcity or '').lower() or 'cantonment' in (road or '').lower() or 'ramgarh' in (rcity or '').lower())
                    if is_cantonment:
                        rcity = "Namkum"
                        road = "RIADA Road"
                        rpincode = "834001"
                        ip_lat = 23.3555
                        ip_lon = 85.3609
                        primary = "RIADA Road"
                        full_display = "RIADA Road, Namkum"
                        r_full_addr = "RIADA Road, Namkum, Ranchi, Jharkhand, 834001, India"
                    else:
                        primary = f"{road}" if road else rcity
                        full_display = f"{primary}, {rcity}" if road and primary != rcity else f"{rcity}, {rstate}"
                        r_full_addr = rdata.get('display_name', '')
                    
                    detected = {
                        'name': full_display,
                        'primary': primary,
                        'secondary': f"{rcity}, {rstate} {rpincode}".strip(),
                        'full_address': r_full_addr,
                        'city': rcity,
                        'state': rstate,
                        'lat': ip_lat,
                        'lon': ip_lon,
                        'source': 'live_network_reverse'
                    }
            except Exception:
                pass

        if not detected and city:
            detected = {
                'name': f"{city}, {region}",
                'primary': city,
                'secondary': region,
                'city': city,
                'state': region,
                'lat': ip_lat,
                'lon': ip_lon,
                'source': 'network_ip'
            }

    if not detected:
        detected = {
            'name': "Ranchi, Jharkhand",
            'primary': "Main Road, Ranchi",
            'secondary': "Jharkhand 834001",
            'city': "Ranchi",
            'state': "Jharkhand",
            'lat': 23.3555,
            'lon': 85.3609,
            'source': 'fallback'
        }

    return JsonResponse(detected)


def search_locations_api(request):
    from django.http import JsonResponse
    import urllib.request, urllib.parse, json
    
    q = request.GET.get('q', '').strip()
    if not q or len(q) < 2:
        return JsonResponse({'results': []})

    results = []
    try:
        encoded_q = urllib.parse.quote(q)
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={encoded_q}&countrycodes=in&limit=8&addressdetails=1"
        req = urllib.request.Request(url, headers={'User-Agent': 'SuguLiveApp/1.0'})
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            data = json.loads(resp.read().decode())
            for item in data:
                addr = item.get('address', {})
                road = addr.get('road') or addr.get('suburb') or addr.get('neighbourhood') or addr.get('village') or item.get('name')
                city = addr.get('city') or addr.get('town') or addr.get('county') or addr.get('state_district') or ''
                state = addr.get('state', '')
                postcode = addr.get('postcode', '')
                
                primary = f"{road}" if road else (city or item.get('name'))
                sec = f"{city}, {state} {postcode}".strip(' ,')
                disp = f"{primary}, {city}" if city and primary != city else f"{primary}, {state}"
                
                results.append({
                    'name': disp,
                    'primary': primary,
                    'secondary': sec,
                    'lat': item.get('lat'),
                    'lon': item.get('lon')
                })
    except Exception as e:
        pass

    return JsonResponse({'results': results})


