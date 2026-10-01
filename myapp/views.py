from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.db.models import Q, Sum, Count, Avg, Prefetch
import os
import mimetypes
from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.template import TemplateDoesNotExist
from .models import (
    VendorProfile, QuickService, Job, Bid, Subscription, Category, Location, 
    UserProfile, Message, GlobalSettings, SiteBranding, HeroSection, 
    QuickServiceCard, FeaturedProjectCard, PackageCard, Testimonial, TrustMetric,
    VendorWallet, WalletTransaction, PayoutRequest, VendorKYC,
    DisputeTicket, DisputeMessage, JobCompletionProof, ServiceReview, ServiceBooking,
    BidCreditTransaction, BidPlan
)

User = get_user_model()

import json
from django.utils import timezone
from datetime import datetime

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
            if selected_state and selected_state != 'all':
                admin_state = selected_state
                co_admins = User.objects.filter(role='ADMIN', assigned_state=admin_state)
            else:
                admin_state = u.assigned_state or None
                if admin_state:
                    co_admins = User.objects.filter(role='ADMIN', assigned_state=admin_state)

    return admin_state, is_area_admin, available_states, co_admins

def get_user_dashboard_context(user):
    name = user.get_full_name() or user.username
    initials = (user.first_name[:1].upper() + user.last_name[:1].upper()) if (user.first_name and user.last_name) else (user.first_name[:2].upper() if user.first_name else user.username[:2].upper())
    date_str = datetime.now().strftime("%A, %d %B %Y")
    
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

    recent_qs = qs_bookings.select_related('quick_service', 'vendor', 'vendor__vendor_profile').order_by('-created_at')[:5]
    for b in recent_qs:
        b.selected_vendor_name = b.vendor.vendor_profile.company_name if hasattr(b.vendor, 'vendor_profile') and b.vendor.vendor_profile.company_name else (b.vendor.get_full_name() or b.vendor.username)
        b.is_vendor_verified = b.vendor_id in approved_kyc_vendor_ids

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
        'user_location': 'Ranchi, Jharkhand',
        'active_qs': active_qs,
        'active_jobs': active_jobs,
        'pending_quotations': pending_quotations,
        'selected_vendors': selected_vendors,
        'completed_qs': completed_qs,
        'completed_jobs': completed_jobs,
        'recent_qs': recent_qs,
        'recent_jobs': recent_jobs,
        'recent_activity': activity_items,
    }

def dashboard_view(request, path=''):
    if not path:
        path = 'index'
        
    if path.endswith('.html'):
        path = path[:-5]

    # Enforce authentication for user/ pages before proceeding
    if path.startswith('user/') and not request.user.is_authenticated:
        return redirect('register_user')

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

            if booking_key:
                if str(booking_key).startswith('job:'):
                    job_id = str(booking_key).split(':')[1]
                elif str(booking_key).startswith('qs:'):
                    qs_id = str(booking_key).split(':')[1]

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

            title = request.POST.get('title', '').strip() or "Quick Home Service"
            category_id = request.POST.get('category_id')
            base_price = request.POST.get('base_price', '199')
            description = request.POST.get('description', '').strip()
            locality = request.POST.get('locality', '').strip() or "Lalpur, Ranchi"
            lat_val = request.POST.get('latitude')
            lon_val = request.POST.get('longitude')
            radius_val = request.POST.get('service_radius_km', 10.0)

            try: lat = float(lat_val) if lat_val else 23.3697
            except (ValueError, TypeError): lat = 23.3697

            try: lon = float(lon_val) if lon_val else 85.3346
            except (ValueError, TypeError): lon = 85.3346

            try: radius = float(radius_val) if radius_val else 10.0
            except (ValueError, TypeError): radius = 10.0

            try: default_price = float(base_price) if base_price else 199.0
            except (ValueError, TypeError): default_price = 199.0

            cat_obj = Category.objects.filter(id=category_id).first() if category_id else Category.objects.filter(status='active').first()

            # Parse Package Options
            service_packages = []
            packages_json = request.POST.get('packages_json')
            if packages_json:
                try:
                    parsed_pkgs = json.loads(packages_json)
                    if isinstance(parsed_pkgs, list):
                        for p in parsed_pkgs:
                            if isinstance(p, dict) and p.get('name'):
                                p_price = float(p.get('price', default_price))
                                p_orig = float(p.get('original_price', round(p_price * 1.3)))
                                service_packages.append({
                                    'name': str(p.get('name')).strip(),
                                    'price': p_price,
                                    'original_price': p_orig,
                                    'desc': str(p.get('desc', '')).strip()
                                })
                except Exception:
                    pass

            if not service_packages:
                pkg_names = request.POST.getlist('package_name[]')
                pkg_prices = request.POST.getlist('package_price[]')
                pkg_orig_prices = request.POST.getlist('package_orig_price[]')
                pkg_descs = request.POST.getlist('package_desc[]')

                for i, name in enumerate(pkg_names):
                    if not name.strip():
                        continue
                    try: p_val = float(pkg_prices[i]) if i < len(pkg_prices) else default_price
                    except (ValueError, TypeError): p_val = default_price

                    try: orig_val = float(pkg_orig_prices[i]) if i < len(pkg_orig_prices) and pkg_orig_prices[i] else round(p_val * 1.3)
                    except (ValueError, TypeError): orig_val = round(p_val * 1.3)

                    d_val = pkg_descs[i].strip() if i < len(pkg_descs) else ""
                    service_packages.append({
                        'name': name.strip(),
                        'price': p_val,
                        'original_price': orig_val,
                        'desc': d_val
                    })

            if not service_packages:
                service_packages = [
                    {
                        'name': 'Standard Service',
                        'price': default_price,
                        'original_price': round(default_price * 1.3),
                        'desc': description or f"Full {title} service by verified professional."
                    }
                ]

            # Lowest package price sets the starting base rate
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
                    "30 days Suggu protection warranty on all workmanship"
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
                status='active'
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
    admin_subfolders = ['users/', 'quick-services/', 'jobs/', 'bidding/', 'subscriptions/', 'payments/', 'reviews/', 'complaints/', 'reports/', 'master/']
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
    
    if path.startswith('vendor/') and request.user.is_authenticated:
        try:
            from .wallet_services import get_or_create_wallet
            wallet = get_or_create_wallet(request.user)
            context['wallet_balance'] = f"{wallet.available_balance:.2f}"
            context['vendor_wallet'] = wallet
            vendor_profile = getattr(request.user, 'vendor_profile', None)
            if vendor_profile:
                name = vendor_profile.company_name or request.user.get_full_name() or request.user.username
                context['vendor_name'] = name
                context['vendor_initials'] = name[:2].upper() if name else "VN"
                context['vendor_location'] = vendor_profile.location or "Unknown Location"
                context['vendor_type'] = "Company Vendor" if vendor_profile.company_name else "Individual Vendor"
                context['profile_image_url'] = vendor_profile.profile_image.url if vendor_profile.profile_image else None
                context['remaining_credits'] = getattr(vendor_profile, 'available_bids', 5)
                context['available_bids'] = getattr(vendor_profile, 'available_bids', 5)
            else:
                name = request.user.get_full_name() or request.user.username
                context['vendor_name'] = name
                context['vendor_initials'] = name[:2].upper() if name else "VN"
                context['vendor_location'] = "Unknown Location"
                context['vendor_type'] = "Vendor"
                context['profile_image_url'] = None
                context['remaining_credits'] = 5
        except Exception:
            pass
            
    # Inject dynamic user data
    if 'master/categories' in path:
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
            cand_qs = ServiceBooking.objects.filter(customer=request.user, status__in=['selected', 'completed']).select_related('category').order_by('-created_at')

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
                sel = Bid.objects.filter(quick_service=q, status__in=['selected', 'completed']).first()
                if sel:
                    q.review_vendor = sel.vendor
                    q.has_reviewed = ServiceReview.objects.filter(customer=request.user, quick_service=q).exists()
                    valid_cand_qs.append(q)

            context['candidate_jobs'] = valid_cand_jobs
            context['candidate_quick_services'] = valid_cand_qs

            preselected_job_id = request.GET.get('job_id')
            preselected_qs_id = request.GET.get('quick_service_id')
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
                target_qs = ServiceBooking.objects.filter(id=preselected_qs_id, customer=request.user).first()
                if target_qs:
                    sel = Bid.objects.filter(quick_service=target_qs, status__in=['selected', 'completed']).first()
                    if sel:
                        target_vendor = sel.vendor

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
            
            if first_name:
                request.user.first_name = first_name
            if email:
                request.user.email = email
            request.user.save()
            
            if phone_number:
                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                profile.phone_number = phone_number
                profile.save()
                
            return redirect('/user/profile/index.html')

    if path == 'vendor/profile/index' or path == 'vendor/profile':
        if request.user.is_authenticated:
            try:
                v_profile = request.user.vendor_profile
            except Exception:
                v_profile = None
            qs_count = QuickService.objects.filter(bids__vendor=request.user, status='completed').distinct().count()
            jobs_count = Job.objects.filter(bids__vendor=request.user, status='completed').distinct().count()
            total_bids = Bid.objects.filter(vendor=request.user).count()
            context.update({
                'completed_qs': qs_count,
                'completed_jobs': jobs_count,
                'total_bids': total_bids,
                'profile': v_profile,
            })

    if path == 'vendor/profile/edit':
        if request.method == 'POST' and request.user.is_authenticated:
            company_name = request.POST.get('company_name')
            category = request.POST.get('category')
            location = request.POST.get('location')
            experience = request.POST.get('experience')
            about = request.POST.get('about')
            
            try:
                profile = request.user.vendor_profile
                if company_name is not None:
                    profile.company_name = company_name
                if category is not None:
                    profile.category = category
                if location is not None:
                    profile.location = location
                if experience is not None:
                    try:
                        profile.experience = int(experience)
                    except:
                        pass
                if about is not None:
                    profile.about = about
                profile.save()
            except Exception:
                pass
            return redirect('/vendor/profile/index.html')

    if path == 'vendor/kyc/index' or path == 'vendor/kyc':
        from .models import VendorKYC
        if request.user.is_authenticated:
            kyc = VendorKYC.objects.filter(vendor=request.user).first()
            if not kyc:
                kyc = VendorKYC(vendor=request.user)
                
            if request.method == 'POST':
                kyc.id_type = request.POST.get('id_type', 'aadhaar')
                kyc.id_number = request.POST.get('id_number')
                
                if 'id_document_front' in request.FILES:
                    kyc.id_document_front = request.FILES['id_document_front']
                if 'id_document_back' in request.FILES:
                    kyc.id_document_back = request.FILES['id_document_back']
                if 'business_license' in request.FILES:
                    kyc.business_license = request.FILES['business_license']
                if 'gst_certificate' in request.FILES:
                    kyc.gst_certificate = request.FILES['gst_certificate']
                
                kyc.status = 'pending'
                kyc.save()
                
                return redirect('/vendor/kyc/index.html')
            
            context['kyc'] = kyc

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

    if path == 'user/messages/index' or path == 'user/messages':
        if request.user.is_authenticated:
            # Get distinct users the current user has chatted with
            sent_to = Message.objects.filter(sender=request.user).values_list('receiver', flat=True)
            received_from = Message.objects.filter(receiver=request.user).values_list('sender', flat=True)
            vendor_ids = set(sent_to) | set(received_from)
            
            conversations = []
            for v_id in vendor_ids:
                try:
                    vendor_user = User.objects.get(id=v_id)
                    latest_message = Message.objects.filter(
                        Q(sender=request.user, receiver=vendor_user) | 
                        Q(sender=vendor_user, receiver=request.user)
                    ).order_by('-created_at').first()
                    
                    unread_count = Message.objects.filter(sender=vendor_user, receiver=request.user, is_read=False).count()
                    
                    try:
                        profile = vendor_user.vendor_profile
                        company_name = profile.company_name or vendor_user.get_full_name() or vendor_user.username
                    except:
                        company_name = vendor_user.get_full_name() or vendor_user.username
                        
                    conversations.append({
                        'vendor_id': vendor_user.id,
                        'name': company_name,
                        'initials': company_name[:2].upper() if company_name else 'V',
                        'latest_message': latest_message,
                        'unread_count': unread_count,
                    })
                except User.DoesNotExist:
                    continue
                    
            # Sort conversations by latest message time descending
            conversations.sort(key=lambda x: x['latest_message'].created_at if x['latest_message'] else timezone.now(), reverse=True)
            context['conversations'] = conversations

    if path == 'user/messages/chat':
        vendor_id = request.GET.get('vendor_id')
        if request.method == 'POST':
            content = request.POST.get('content')
            if content and vendor_id:
                try:
                    vendor_user = User.objects.get(id=vendor_id)
                    Message.objects.create(
                        sender=request.user,
                        receiver=vendor_user,
                        content=content
                    )
                except User.DoesNotExist:
                    pass
            return redirect(f'/user/messages/chat.html?vendor_id={vendor_id}')
            
        if vendor_id and request.user.is_authenticated:
            try:
                vendor_user = User.objects.get(id=vendor_id)
                # Mark unread messages as read
                Message.objects.filter(sender=vendor_user, receiver=request.user, is_read=False).update(is_read=True)
                
                chat_msgs = Message.objects.filter(
                    Q(sender=request.user, receiver=vendor_user) | 
                    Q(sender=vendor_user, receiver=request.user)
                ).order_by('created_at')
                
                try:
                    profile = vendor_user.vendor_profile
                    company_name = profile.company_name or vendor_user.get_full_name() or vendor_user.username
                    category = profile.category
                except:
                    company_name = vendor_user.get_full_name() or vendor_user.username
                    category = 'General'
                    
                context['chat_vendor'] = {
                    'id': vendor_user.id,
                    'name': company_name,
                    'initials': company_name[:2].upper() if company_name else 'V',
                    'category': category
                }
                context['chat_messages'] = chat_msgs
            except User.DoesNotExist:
                context['chat_vendor'] = None
                context['chat_messages'] = []

    if path == 'vendor/jobs/available':
        available_jobs = Job.objects.filter(status='open').order_by('-created_at')
        context['available_jobs'] = available_jobs

    if path == 'vendor/jobs/bid-details':
        bid_id = request.GET.get('bid_id')
        if bid_id:
            try:
                bid = Bid.objects.select_related('job', 'job__user').get(id=bid_id, vendor=request.user)
                context['bid'] = bid
            except Bid.DoesNotExist:
                pass

    if path == 'vendor/jobs/selected-jobs':
        selected_bids = Bid.objects.filter(vendor=request.user, status__in=['selected', 'completed']).select_related('job', 'quick_service', 'job__user', 'quick_service__user').order_by('-created_at')
        context['selected_bids'] = selected_bids

    if path == 'vendor/jobs/details' or path == 'vendor/jobs/send-quotation':
        job_id = request.GET.get('id') or request.GET.get('job_id') or request.POST.get('job_id') or request.POST.get('id')
        
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
                        if hasattr(request.user, 'vendor_profile') and request.user.vendor_profile.available_bids > 0:
                            if not Bid.objects.filter(job=job, vendor=request.user).exists():
                                Bid.objects.create(
                                    vendor=request.user,
                                    job=job,
                                    amount=amount,
                                    estimated_time=estimated_time,
                                    proposal=proposal,
                                    attachment=attachment
                                )
                                request.user.vendor_profile.available_bids -= 1
                                request.user.vendor_profile.save(update_fields=['available_bids'])

                                # Record dynamic credit transaction
                                BidCreditTransaction.objects.create(
                                    vendor=request.user,
                                    transaction_type='used',
                                    credits=-1,
                                    description=f"Bid placed on {job.title}",
                                    related_job=job
                                )
                                messages.success(request, f"Quotation submitted successfully! 1 credit deducted ({request.user.vendor_profile.available_bids} credits remaining).")
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
            context['my_services'] = QuickService.objects.filter(vendor=request.user).select_related('category').order_by('-created_at')
            context['categories'] = Category.objects.filter(status='active').order_by('name')

    if path in ['vendor/bookings', 'vendor/bookings/index', 'vendor/bookings/index.html']:
        if request.method == 'POST' and request.user.is_authenticated:
            booking_id = request.POST.get('booking_id')
            action = request.POST.get('action') # e.g. accept, complete, cancel
            if booking_id and action:
                try:
                    booking = ServiceBooking.objects.get(id=booking_id, vendor=request.user)
                    if action == 'accept':
                        booking.status = 'accepted'
                    elif action == 'complete':
                        booking.status = 'completed'
                    elif action == 'cancel':
                        booking.status = 'cancelled'
                    booking.save(update_fields=['status'])
                    messages.success(request, f"Booking status updated to {booking.get_status_display()}.")
                except ServiceBooking.DoesNotExist:
                    pass
            return redirect('/vendor/bookings/index.html')

        if request.user.is_authenticated:
            context['my_bookings'] = ServiceBooking.objects.filter(vendor=request.user).select_related('customer', 'quick_service').order_by('-created_at')
    if path in ['user/services/browse', 'user/services/browse.html']:
        if request.user.is_authenticated:
            context['services'] = QuickService.objects.filter(status='open').select_related('vendor', 'category').order_by('-created_at')
            context['categories'] = Category.objects.filter(status='active')

    if path in ['user/services/book', 'user/services/book.html']:
        if request.method == 'POST' and request.user.is_authenticated:
            qs_id = request.POST.get('qs_id')
            package_name = request.POST.get('package_name', 'Standard')
            total_amount = request.POST.get('total_amount', 0)
            scheduled_date = request.POST.get('scheduled_date')
            scheduled_time = request.POST.get('scheduled_time', '')
            service_address = request.POST.get('service_address')
            
            if qs_id and scheduled_date and service_address:
                try:
                    qs = QuickService.objects.get(id=qs_id)
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
                    messages.success(request, "Service booked successfully! Awaiting vendor acceptance.")
                    return redirect('/user/services/my-bookings.html')
                except QuickService.DoesNotExist:
                    pass

        qs_id = request.GET.get('id') or request.GET.get('service_id')
        if qs_id:
            try:
                context['service'] = QuickService.objects.select_related('vendor').get(id=qs_id)
                context['selected_pkg'] = request.GET.get('pkg', 'Standard Service')
                context['selected_amount'] = request.GET.get('amount')
            except QuickService.DoesNotExist:
                return redirect('/services/browse')

    if path in ['user/services/my-bookings', 'user/services/my-bookings.html']:
        if request.user.is_authenticated:
            context['my_bookings'] = ServiceBooking.objects.filter(customer=request.user).select_related('vendor', 'quick_service').order_by('-created_at')

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
                    qs_uids = QuickService.objects.filter(Q(location__state__iexact=admin_state) | Q(address__icontains=admin_state)).values_list('user_id', flat=True)
                    cust_qs = cust_qs.filter(Q(id__in=set(job_uids).union(set(qs_uids))) | Q(assigned_state__iexact=admin_state))
                target_user = cust_qs.first()

            if target_user:
                # Strict territory authorization check for Area Admin
                if is_area_admin and admin_state:
                    user_matches_state = bool(target_user.assigned_state and target_user.assigned_state.lower() == admin_state.lower())
                    has_job_in_state = Job.objects.filter(user=target_user).filter(Q(location__state__iexact=admin_state) | Q(address__icontains=admin_state)).exists()
                    has_qs_in_state = ServiceBooking.objects.filter(customer=target_user).filter(Q(location__state__iexact=admin_state) | Q(address__icontains=admin_state)).exists()

                    if not (user_matches_state or has_job_in_state or has_qs_in_state):
                        messages.error(request, f"Access Denied: Customer '{target_user.get_full_name() or target_user.username}' is outside your assigned territory ({admin_state}).")
                        return redirect('/admin-dashboard/users/users.html')

                mobile = '—'
                try:
                    if hasattr(target_user, 'user_profile') and target_user.user_profile.phone_number:
                        mobile = target_user.user_profile.phone_number
                except Exception:
                    pass

                cust_qs_list = ServiceBooking.objects.filter(customer=target_user).select_related('category', 'location').order_by('-created_at')
                cust_jobs_list = Job.objects.filter(user=target_user).select_related('category', 'location').order_by('-created_at')
                if admin_state:
                    cust_qs_list = cust_qs_list.filter(Q(location__state__iexact=admin_state) | Q(address__icontains=admin_state))
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
                    total_bids = total_bids.filter(Q(job__location__state__iexact=admin_state) | Q(quick_service__location__state__iexact=admin_state) | Q(job__address__icontains=admin_state) | Q(quick_service__address__icontains=admin_state))

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
                qs_uids = QuickService.objects.filter(Q(location__state__iexact=admin_state) | Q(address__icontains=admin_state)).values_list('user_id', flat=True)
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
                service = QuickService.objects.select_related('user', 'category', 'location').get(id=qs_id)

                # Strict territory check for Area Admin
                admin_state, is_area_admin, available_states, co_admins = get_admin_state_context(request)
                if is_area_admin and admin_state:
                    qs_in_state = (service.location and service.location.state and service.location.state.lower() == admin_state.lower()) or (admin_state.lower() in (service.address or '').lower()) or (bool(service.user.assigned_state and service.user.assigned_state.lower() == admin_state.lower()))
                    if not qs_in_state:
                        messages.error(request, f"Access Denied: Quick Service is outside your assigned territory ({admin_state}).")
                        return redirect('/quick-services/index.html')

                context['service'] = service
                
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

    elif 'quick-services' in path:
        from django.db.models import Count, Prefetch
        admin_state, is_area_admin, available_states, co_admins = get_admin_state_context(request)
        context['admin_state'] = admin_state
        context['is_area_admin'] = is_area_admin
        quick_services = QuickService.objects.exclude(category__service_type='job').select_related('user', 'category', 'location').annotate(vendor_requests_count=Count('bids')).prefetch_related(Prefetch('bids', queryset=Bid.objects.filter(status='selected').select_related('vendor', 'vendor__vendor_profile'), to_attr='selected_bids')).order_by('-created_at')
        if admin_state:
            quick_services = quick_services.filter(Q(location__state__iexact=admin_state) | Q(address__icontains=admin_state))
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
                'customer': u.get_full_name() or u.username,
                'customerMobile': mobile,
                'customerId': f'USR-{u.id:04d}',
                'avatar_class': f'av-{(u.id % 5) + 1}',
                'title': qs.title,
                'category': qs.category.name if getattr(qs, 'category', None) else 'Uncategorized',
                'location': f"{qs.location.city}, {qs.location.state}" if getattr(qs, 'location', None) else (admin_state or 'Unknown'),
                'budget': float(qs.budget) if qs.budget else 0,
                'vendorRequests': getattr(qs, 'vendor_requests_count', 0),
                'selectedVendor': selected_vendor_name,
                'status': qs.status,
                'created': qs.created_at.strftime('%Y-%m-%d') if qs.created_at else 'Unknown'
            })
        context['quick_services_json'] = json.dumps(qs_data)
        context['quick_services_list'] = qs_data
        
        active_statuses = {'open', 'active', 'progress', 'selected'}
        closed_statuses = {'completed', 'cancelled', 'closed'}
        context['active_qs'] = [qs for qs in qs_data if qs['status'] in active_statuses]
        context['closed_qs'] = [qs for qs in qs_data if qs['status'] in closed_statuses]
        
        
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
            if vendor_profile:
                vendor_profile.company_name = request.POST.get('company_name', vendor_profile.company_name)
                vendor_profile.address = request.POST.get('address', vendor_profile.address)
                vendor_profile.about = request.POST.get('about', vendor_profile.about)
                
                profile_image_base64 = request.POST.get('profile_image_base64')
                if profile_image_base64:
                    import base64
                    from django.core.files.base import ContentFile
                    # Format: data:image/png;base64,iVBORw0KGgo...
                    format, imgstr = profile_image_base64.split(';base64,') 
                    ext = format.split('/')[-1] 
                    vendor_profile.profile_image = ContentFile(base64.b64decode(imgstr), name=f'profile_{u.id}.{ext}')
                elif 'profile_image' in request.FILES:
                    vendor_profile.profile_image = request.FILES['profile_image']
                    
                vendor_profile.save()
            
            # Update user details
            u.first_name = request.POST.get('first_name', u.first_name)
            u.email = request.POST.get('email', u.email)
            u.save()
            
            # Update UserProfile mobile
            try:
                user_profile, _ = UserProfile.objects.get_or_create(user=u)
                new_mobile = request.POST.get('phone_number') or request.POST.get('mobile')
                if new_mobile:
                    user_profile.phone_number = new_mobile.strip()
                    user_profile.save()
            except Exception:
                pass
                
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
                qs_uids = QuickService.objects.filter(Q(location__state__iexact=admin_state) | Q(address__icontains=admin_state)).values_list('user_id', flat=True)
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
            
    if 'messages/index' in path or 'messages/chat' in path:
        u = request.user
        if not u.is_authenticated:
            return redirect('/login/')
            
        is_vendor = 'vendor' in path
        
        # Determine conversations (unique opposite party)
        if is_vendor:
            # For vendor, conversations are with Users (role='USER')
            conversations_qs = Message.objects.filter(
                Q(sender=u) | Q(receiver=u)
            ).values('sender', 'receiver').distinct()
            
            contact_ids = set()
            for c in conversations_qs:
                if c['sender'] != u.id: contact_ids.add(c['sender'])
                if c['receiver'] != u.id: contact_ids.add(c['receiver'])
                
            contacts = User.objects.filter(id__in=contact_ids, role='USER')
        else:
            # For user, conversations are with Vendors
            conversations_qs = Message.objects.filter(
                Q(sender=u) | Q(receiver=u)
            ).values('sender', 'receiver').distinct()
            
            contact_ids = set()
            for c in conversations_qs:
                if c['sender'] != u.id: contact_ids.add(c['sender'])
                if c['receiver'] != u.id: contact_ids.add(c['receiver'])
                
            contacts = User.objects.filter(id__in=contact_ids, role='VENDOR')
            
        conversations_list = []
        for contact in contacts:
            latest_msg = Message.objects.filter(
                Q(sender=u, receiver=contact) | Q(sender=contact, receiver=u)
            ).order_by('-created_at').first()
            
            unread_count = Message.objects.filter(sender=contact, receiver=u, is_read=False).count()
            
            name = contact.get_full_name() or contact.username
            if not is_vendor:
                try:
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
            
        conversations_list.sort(key=lambda x: x['latest_message'].created_at if x['latest_message'] else timezone.now(), reverse=True)
        context['conversations'] = conversations_list
        
        if 'messages/chat' in path:
            other_user_id = request.GET.get('vendor_id') or request.GET.get('user_id')
            if not other_user_id and conversations_list:
                other_user_id = conversations_list[0]['id']
                
            if other_user_id:
                other_user = User.objects.filter(id=other_user_id).first()
                if other_user:
                    # Mark messages as read
                    Message.objects.filter(sender=other_user, receiver=u, is_read=False).update(is_read=True)
                    
                    if request.method == 'POST':
                        content = request.POST.get('content')
                        attachment = request.FILES.get('attachment')
                        if content or attachment:
                            msg = Message.objects.create(
                                sender=u,
                                receiver=other_user,
                                content=content,
                                attachment=attachment
                            )
                            
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
                                    'message': msg.content + extra,
                                    'sender_id': u.id,
                                    'sender_name': u.get_full_name() or u.username,
                                    'time': msg.created_at.strftime("%I:%M %p").lstrip('0')
                                }
                            )
                            
                            # Redirect to prevent duplicate submission
                            param = '?vendor_id=' + str(other_user.id) if not is_vendor else '?user_id=' + str(other_user.id)
                            return redirect('/' + path + '.html' + param)
                            
                    chat_messages = Message.objects.filter(
                        Q(sender=u, receiver=other_user) | Q(sender=other_user, receiver=u)
                    ).order_by('created_at')
                    context['chat_messages'] = chat_messages
                    
                    name = other_user.get_full_name() or other_user.username
                    category = 'User'
                    if not is_vendor:
                        try:
                            name = other_user.vendor_profile.company_name or name
                            category = other_user.vendor_profile.category
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
        context.update(get_user_dashboard_context(request.user))

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
            context['selected_bids'] = Bid.objects.filter(vendor=request.user, status__in=['selected', 'completed']).select_related('job', 'quick_service', 'job__user', 'quick_service__user').order_by('-created_at')

    if 'vendor/jobs/bid-details' in path:
        bid_id = request.GET.get('bid_id') or request.GET.get('id')
        if bid_id and request.user.is_authenticated:
            try:
                context['bid'] = Bid.objects.select_related('job', 'job__user', 'quick_service', 'quick_service__user').get(id=bid_id, vendor=request.user)
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
            qs_uids = QuickService.objects.filter(Q(location__state__iexact=admin_state) | Q(address__icontains=admin_state)).values_list('user_id', flat=True)
            customers_qs = customers_qs.filter(Q(id__in=set(job_uids).union(set(qs_uids))) | Q(assigned_state__iexact=admin_state))
        context['customers'] = customers_qs.order_by('-date_joined')

    if 'users/kyc-approvals' in path:
        from .models import VendorKYC
        admin_state, is_area_admin, available_states, co_admins = get_admin_state_context(request)
        context['admin_state'] = admin_state
        context['is_area_admin'] = is_area_admin
        kycs = VendorKYC.objects.select_related('vendor', 'vendor__vendor_profile').all()
        if admin_state:
            kycs = kycs.filter(Q(vendor__vendor_profile__location__icontains=admin_state) | Q(vendor__assigned_state__iexact=admin_state))
        
        status_filter = request.GET.get('status', 'pending')
        if status_filter != 'all':
            kycs = kycs.filter(status=status_filter)
        
        context['kycs'] = kycs.order_by('-id')

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
    qs_qs = QuickService.objects.select_related('user', 'category', 'location')
    bid_qs = Bid.objects.select_related('vendor', 'job', 'quick_service', 'vendor__vendor_profile')
    sub_qs = Subscription.objects.select_related('vendor', 'vendor__vendor_profile')

    if admin_state:
        job_qs = job_qs.filter(Q(location__state__iexact=admin_state) | Q(address__icontains=admin_state))
        qs_qs = qs_qs.filter(Q(location__state__iexact=admin_state) | Q(address__icontains=admin_state))
        vendor_qs = vendor_qs.filter(Q(location__icontains=admin_state) | Q(user__assigned_state__iexact=admin_state))
        
        state_customer_ids = set(job_qs.values_list('user_id', flat=True)).union(
            set(qs_qs.values_list('user_id', flat=True))
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
        
    services_qs = QuickService.objects.filter(status='active').select_related('vendor', 'category').order_by('-created_at')
    
    if selected_category:
        services_qs = services_qs.filter(category_id=selected_category.id)
        
    if search_query:
        services_qs = services_qs.filter(title__icontains=search_query)
        
    if sub_query:
        services_qs = services_qs.filter(title__icontains=sub_query)

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
            "30 days Suggu protection warranty on all workmanship"
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
            'packages': packages
        })
        
    context = {
        'services': enriched_services,
        'categories': categories,
        'selected_category': selected_category,
        'selected_category_id': selected_category.id if selected_category else None,
        'search_query': search_query,
        'sub_query': sub_query,
        'user_lat': user_lat,
        'user_lon': user_lon,
        'services_json': json.dumps(enriched_services),
        'user': request.user
    }
    return render(request, 'browse.html', context)

    
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

    categories = Category.objects.filter(status='active').order_by('name')
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
            login(request, user)
            return redirect('user_dashboard')
    
    return render(request, 'register_user.html', {'error': error})

def register_vendor_view(request):
    error = None
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        company_name = request.POST.get('company_name', '').strip()
        email = request.POST.get('email', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        category = request.POST.get('category', '').strip()
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
        
        if password != confirm_password:
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
                category=category,
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

    context = {
        'error': error,
        'categories': Category.objects.filter(status='active').order_by('name'),
        'locations_json': json.dumps(locations_dict),
        'states': sorted(locations_dict.keys()),
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

    available_qs = QuickService.objects.filter(status='open').count()
    available_jobs = Job.objects.filter(status='open').count()
    
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
    
    context.update({
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
        'is_kyc_verified': bool(kyc and kyc.status == 'approved'),
        'recent_transactions': wallet.transactions.all().order_by('-created_at')[:4],
    })

    # Fetch recent items
    context['recent_quick_services'] = QuickService.objects.filter(status='open').order_by('-created_at')[:3]
    context['recent_jobs'] = Job.objects.filter(status='open').order_by('-created_at')[:2]

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

    context = get_user_dashboard_context(request.user)
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

def manage_location_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        loc_id = request.POST.get('id')
        
        if action == 'delete':
            if loc_id:
                Location.objects.filter(id=loc_id).delete()
        else:
            state = request.POST.get('state_new', '').strip()
            if not state:
                state = request.POST.get('state', '').strip()
            city = request.POST.get('city', '').strip()
            status = request.POST.get('status', 'active')
            
            if state and city:
                if loc_id:
                    Location.objects.filter(id=loc_id).update(state=state, city=city, status=status)
                else:
                    Location.objects.create(state=state, city=city, status=status)
        
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
        kyc.status = 'approved'
        kyc.reviewed_by = request.user
        kyc.save()
        messages.success(request, f"KYC for {kyc.vendor.username} approved.")
    return redirect('/admin-dashboard/users/kyc-approvals.html')

@login_required
def reject_kyc_view(request, kyc_id):
    if request.method == 'POST':
        if request.user.role != 'ADMIN' and not request.user.is_superuser:
            return HttpResponseForbidden("Access Denied")
        from .models import VendorKYC
        kyc = get_object_or_404(VendorKYC, id=kyc_id)
        kyc.status = 'rejected'
        kyc.reviewed_by = request.user
        kyc.admin_notes = request.POST.get('admin_notes', '')
        kyc.save()
        messages.warning(request, f"KYC for {kyc.vendor.username} rejected.")
    return redirect('/admin-dashboard/users/kyc-approvals.html')

def detect_location_api(request):
    from django.http import JsonResponse
    import urllib.request, urllib.parse, json

    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    detected = None

    # If coordinates provided directly from client GPS
    if lat and lon:
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
            req = urllib.request.Request(url, headers={'User-Agent': 'SugguLiveApp/1.0'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode())
                addr = data.get('address', {})
                road = addr.get('road') or addr.get('suburb') or addr.get('neighbourhood') or addr.get('village')
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
            req = urllib.request.Request(url, headers={'User-Agent': 'SugguLiveApp/1.0'})
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
                req = urllib.request.Request(url, headers={'User-Agent': 'SugguLiveApp/1.0'})
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
                req = urllib.request.Request(url, headers={'User-Agent': 'SugguLiveApp/1.0'})
                with urllib.request.urlopen(req, timeout=3) as resp:
                    rdata = json.loads(resp.read().decode())
                    addr = rdata.get('address', {})
                    road = addr.get('road') or addr.get('suburb') or addr.get('neighbourhood') or addr.get('village')
                    rcity = addr.get('city') or addr.get('town') or addr.get('state_district') or city or "Ranchi"
                    rstate = addr.get('state') or region or "Jharkhand"
                    rpincode = addr.get('postcode', '')
                    
                    primary = f"{road}" if road else rcity
                    full_display = f"{primary}, {rcity}" if road and primary != rcity else f"{rcity}, {rstate}"
                    
                    detected = {
                        'name': full_display,
                        'primary': primary,
                        'secondary': f"{rcity}, {rstate} {rpincode}".strip(),
                        'full_address': rdata.get('display_name', ''),
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
        req = urllib.request.Request(url, headers={'User-Agent': 'SugguLiveApp/1.0'})
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


