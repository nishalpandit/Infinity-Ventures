from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
import os
import mimetypes
from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.template import TemplateDoesNotExist
from django.db.models import Sum, Q
from .models import VendorProfile, QuickService, Job, Bid, Subscription, Category, Location, UserProfile, Message
from django.contrib.auth import get_user_model

User = get_user_model()

import json

def dashboard_view(request, path=''):
    if not path:
        path = 'index'
        
    if path.endswith('.html'):
        path = path[:-5]
        
    if request.method == 'POST' and path == 'user/quick-services/create':
        qs = QuickService(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            required_work=request.POST.getlist('required_work[]'),
            budget=request.POST.get('budget', 0),
            shift_availability=request.POST.get('shift_availability'),
            address=request.POST.get('address'),
            additional_requirements=request.POST.get('additional_requirements'),
            contact_name=request.POST.get('contact_name'),
            contact_mobile=request.POST.get('contact_mobile'),
            user=request.user,
            status='open'
        )
        
        cat_id = request.POST.get('category')
        if cat_id: qs.category_id = cat_id
            
        loc_id = request.POST.get('location_id')
        if loc_id: qs.location_id = loc_id
            
        pref_date = request.POST.get('preferred_date')
        if pref_date: qs.preferred_date = pref_date
            
        pref_time = request.POST.get('preferred_time')
        if pref_time: qs.preferred_time = pref_time
            
        qs.save()
        return redirect('/user/quick-services/index')

    if request.method == 'POST' and path == 'user/jobs/create':
        job = Job(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            required_work=request.POST.getlist('required_work[]'),
            scope_of_work=request.POST.get('scope_of_work'),
            materials_details=request.POST.get('materials_details'),
            additional_requirements=request.POST.get('additional_requirements'),
            budget=request.POST.get('budget', 0),
            budget_type=request.POST.get('budget_type'),
            required_time=request.POST.get('required_time'),
            shift_availability=request.POST.get('shift_availability'),
            working_hours=request.POST.get('working_hours'),
            address=request.POST.get('address'),
            pincode=request.POST.get('pincode'),
            contact_name=request.POST.get('contact_name'),
            contact_mobile=request.POST.get('contact_mobile'),
            user=request.user,
            status='open'
        )
        
        cat_id = request.POST.get('category')
        if cat_id: job.category_id = cat_id
            
        loc_id = request.POST.get('location_id')
        if loc_id: job.location_id = loc_id
            
        pref_date = request.POST.get('preferred_start_date')
        if pref_date: job.preferred_start_date = pref_date
            
        exp_comp = request.POST.get('expected_completion')
        if exp_comp: job.expected_completion = exp_comp
            
        job.save()
        return redirect('/user/jobs/index')

    # Map url prefixes to correct template directories
    mapped_path = path
    admin_subfolders = ['users/', 'quick-services/', 'jobs/', 'bidding/', 'subscriptions/', 'payments/', 'reviews/', 'complaints/', 'reports/', 'master/']
    if any(mapped_path.startswith(folder) for folder in admin_subfolders):
        mapped_path = f'admin-dashboard/{mapped_path}'
    elif mapped_path.startswith('user/'):
        mapped_path = mapped_path.replace('user/', 'user-dashboard/', 1)
    elif mapped_path.startswith('vendor/'):
        mapped_path = mapped_path.replace('vendor/', 'fixora-vendor-dashboard/', 1)

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
            vendor_profile = getattr(request.user, 'vendor_profile', None)
            if vendor_profile:
                name = vendor_profile.company_name or request.user.get_full_name() or request.user.username
                context['vendor_name'] = name
                context['vendor_initials'] = name[:2].upper() if name else "VN"
                context['vendor_location'] = vendor_profile.location or "Unknown Location"
                context['vendor_type'] = "Company Vendor" if vendor_profile.company_name else "Individual Vendor"
                context['profile_image_url'] = vendor_profile.profile_image.url if vendor_profile.profile_image else None
                context['remaining_credits'] = getattr(vendor_profile, 'bid_credits', 5)
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
        cat_data = [{'id': c.id, 'name': c.name, 'service_type': c.service_type} for c in active_cats]
        context['categories_json'] = json.dumps(cat_data)
        active_locs = Location.objects.filter(status='active').order_by('state', 'city')
        context['locations'] = active_locs
        loc_data = [{'id': l.id, 'state': l.state, 'city': l.city, 'status': l.status} for l in active_locs]
        context['locations_json'] = json.dumps(loc_data)

    if path == 'user/quick-services/index' or path == 'user/quick-services':
        if request.user.is_authenticated:
            qs_list = QuickService.objects.filter(user=request.user).order_by('-created_at')
            context['quick_services'] = qs_list
            context['status_counts'] = {
                'all': qs_list.count(),
                'open': qs_list.filter(status='open').count(),
                'selected': qs_list.filter(status='selected').count(),
                'progress': qs_list.filter(status='progress').count(),
                'completed': qs_list.filter(status='completed').count(),
                'cancelled': qs_list.filter(status='cancelled').count(),
                'closed': qs_list.filter(status='closed').count(),
            }
            context['active_cats'] = Category.objects.filter(status='active').order_by('name')
        else:
            context['quick_services'] = []
            context['status_counts'] = {'all':0,'open':0,'selected':0,'progress':0,'completed':0,'cancelled':0,'closed':0}
            context['active_cats'] = []

    if path == 'user/quick-services/details':
        qs_id = request.GET.get('id')
        if qs_id:
            try:
                qs = QuickService.objects.select_related('category', 'location').get(id=qs_id, user=request.user)
                context['qs'] = qs
                
                bids = Bid.objects.filter(quick_service_id=qs_id).select_related('vendor', 'vendor__vendor_profile')
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
                        'vendor_name': vendor_name,
                        'vendor_initials': vendor_name[:2].upper(),
                        'vendor_type': 'Service Company' if (profile and profile.company_name) else 'Independent Technician',
                        'rating': float(profile.rating) if (profile and profile.rating) else 0.0,
                        'experience': 5,
                        'completed_jobs': 120,
                    })
                context['bids_data'] = bids_data
                
                selected_bid_data = next((b for b in bids_data if b['bid'].status == 'selected'), None)
                context['selected_bid_data'] = selected_bid_data
                
                if qs.preferred_date and qs.preferred_time:
                    context['preferred_datetime'] = f"{qs.preferred_date.strftime('%d %b %Y')} · {qs.preferred_time.strftime('%I:%M %p')}"
                else:
                    context['preferred_datetime'] = "Not specified"
                    
            except QuickService.DoesNotExist:
                return redirect('/user/quick-services/index')
        else:
            return redirect('/user/quick-services/index')

    if path == 'user/quick-services/quotations':
        qs_id = request.GET.get('id')
        if qs_id:
            bids = Bid.objects.filter(quick_service_id=qs_id).select_related('vendor', 'vendor__vendor_profile')
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
                    'price': float(bid.amount),
                    'estimated_time': bid.estimated_time or '1-2 Days',
                    'vendor_name': vendor_name,
                    'vendor_initials': vendor_name[:2].upper(),
                    'vendor_category': profile.category if profile else 'General',
                    'rating': float(profile.rating) if profile and profile.rating else 0.0,
                    'experience': 5,  # Mocked as we don't have this in profile
                    'completed_jobs': 12, # Mocked
                    'availability': 'available'
                })
            context['quotations_json'] = json.dumps(bids_data)
        else:
            context['quotations_json'] = '[]'

    if path == 'user/jobs/details':
        job_id = request.GET.get('id')
        if job_id:
            try:
                job = Job.objects.select_related('category', 'location').get(id=job_id, user=request.user)
                context['job'] = job
                
                bids = Bid.objects.filter(job_id=job_id).select_related('vendor', 'vendor__vendor_profile')
                
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
                
            except Job.DoesNotExist:
                return redirect('/user/jobs/index')
        else:
            return redirect('/user/jobs/index')

    if path == 'user/jobs/index' or path == 'user/jobs':
        if request.user.is_authenticated:
            job_list = Job.objects.filter(user=request.user).order_by('-created_at')
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
            context['active_cats'] = Category.objects.filter(status='active').order_by('name')
        else:
            context['jobs'] = []
            context['status_counts'] = {'all':0,'open':0,'selected':0,'progress':0,'completed':0,'cancelled':0,'closed':0}
            context['active_cats'] = []
            
    if path == 'user/messages/index' or path == 'user/messages':
        if request.user.is_authenticated:
            # Get distinct users the current user has chatted with
            sent_to = Message.objects.filter(sender=request.user).values_list('receiver', flat=True)
            received_from = Message.objects.filter(receiver=request.user).values_list('sender', flat=True)
            vendor_ids = set(sent_to) | set(received_from)
            
            conversations = []
            for v_id in vendor_ids:
                try:
                    vendor_user = CustomUser.objects.get(id=v_id)
                    latest_message = Message.objects.filter(
                        models.Q(sender=request.user, receiver=vendor_user) | 
                        models.Q(sender=vendor_user, receiver=request.user)
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
                except CustomUser.DoesNotExist:
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
                    vendor_user = CustomUser.objects.get(id=vendor_id)
                    Message.objects.create(
                        sender=request.user,
                        receiver=vendor_user,
                        content=content
                    )
                except CustomUser.DoesNotExist:
                    pass
            return redirect(f'/user/messages/chat.html?vendor_id={vendor_id}')
            
        if vendor_id and request.user.is_authenticated:
            try:
                vendor_user = CustomUser.objects.get(id=vendor_id)
                # Mark unread messages as read
                Message.objects.filter(sender=vendor_user, receiver=request.user, is_read=False).update(is_read=True)
                
                messages = Message.objects.filter(
                    models.Q(sender=request.user, receiver=vendor_user) | 
                    models.Q(sender=vendor_user, receiver=request.user)
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
                context['chat_messages'] = messages
            except CustomUser.DoesNotExist:
                context['chat_vendor'] = None
                context['chat_messages'] = []

    if path == 'vendor/jobs/available':
        available_jobs = Job.objects.filter(status='open').order_by('-created_at')
        context['available_jobs'] = available_jobs

    if path == 'vendor/quick-services/nearby':
        available_qs = QuickService.objects.filter(status='open').order_by('-created_at')
        context['available_qs'] = available_qs


    if 'master/locations' in path:
        context['locations'] = Location.objects.all().order_by('-created_at')
        context['states'] = Location.objects.values_list('state', flat=True).distinct().order_by('state')
        
    if 'users/users' in path or 'users/vendors' in path or 'users/company-vendors' in path or 'users/outsider-vendors' in path:
        if 'users' in path and 'vendors' not in path:
            users_qs = User.objects.filter(role='USER')
            users_data = []
            for u in users_qs:
                try:
                    profile = u.user_profile
                    mobile = profile.phone_number or '—'
                except Exception:
                    mobile = '—'
                    
                quick_services_count = QuickService.objects.filter(user=u).count()
                jobs_count = Job.objects.filter(user=u).count()
                completed_jobs = Job.objects.filter(user=u, status='completed').count()
                
                users_data.append({
                    'id': f'USR-{u.id:04d}',
                    'name': u.get_full_name() or u.username,
                    'email': u.email or '—',
                    'mobile': mobile,
                    'location': 'Unknown',
                    'quickServices': quick_services_count,
                    'jobs': jobs_count,
                    'completedJobs': completed_jobs,
                    'status': 'active' if u.is_active else 'suspended',
                    'registered': u.date_joined.strftime('%Y-%m-%d') if u.date_joined else 'Unknown'
                })
            context['users_json'] = json.dumps(users_data)
            
        if 'vendors' in path:
            vendors = VendorProfile.objects.select_related('user').all()
            vendors_data = []
            for profile in vendors:
                user = profile.user
                v_type = 'company' if profile.company_name else 'outsider'
                total_bids = Bid.objects.filter(vendor=user).count()
                completed_jobs = Job.objects.filter(bids__vendor=user, status='completed').distinct().count()
                
                vendors_data.append({
                    'id': f'VEN-{user.id:04d}',
                    'name': profile.company_name or user.get_full_name() or user.username,
                    'email': user.email or '—',
                    'type': v_type,
                    'contact': '—',
                    'category': profile.category or 'Uncategorized',
                    'location': profile.location or 'Unknown',
                    'totalBids': total_bids,
                    'completedJobs': completed_jobs,
                    'bidCredits': 100, 
                    'status': 'active' if user.is_active else 'suspended',
                    'registered': profile.registered_date.strftime('%Y-%m-%d') if profile.registered_date else 'Unknown'
                })
            context['vendors_json'] = json.dumps(vendors_data)
            
    if 'quick-services' in path:
        quick_services = QuickService.objects.select_related('user').all().order_by('-created_at')
        qs_data = []
        for qs in quick_services:
            u = qs.user
            try:
                u_profile = u.user_profile
                mobile = u_profile.phone_number or '—'
            except Exception:
                mobile = '—'
            
            qs_data.append({
                'id': f'QS-{qs.id:04d}',
                'user': u.get_full_name() or u.username,
                'userMobile': mobile,
                'userId': f'USR-{u.id:04d}',
                'title': qs.title,
                'category': qs.category.name if getattr(qs, 'category', None) else 'Uncategorized',
                'location': f"{qs.location.city}, {qs.location.state}" if getattr(qs, 'location', None) else 'Unknown',
                'budget': float(qs.budget) if qs.budget else 0,
                'vendorRequests': getattr(qs, 'vendor_requests_count', 0),
                'selectedVendor': getattr(qs, 'selected_vendor', '—'),
                'status': qs.status,
                'created': qs.created_at.strftime('%Y-%m-%d') if qs.created_at else 'Unknown'
            })
        context['quick_services_json'] = json.dumps(qs_data)
        
        if 'quick-services/details' in path:
            qs_id_raw = request.GET.get('id')
            if qs_id_raw:
                try:
                    # e.g., 'QS-0001' -> 1
                    qs_id = int(qs_id_raw.replace('QS-', '')) if isinstance(qs_id_raw, str) and qs_id_raw.startswith('QS-') else int(qs_id_raw)
                    service = QuickService.objects.select_related('user', 'category', 'location').get(id=qs_id)
                    context['service'] = service
                    
                    try:
                        u_profile = service.user.user_profile
                        mobile = u_profile.phone_number or '—'
                    except Exception:
                        mobile = '—'
                    context['service_customer_mobile'] = mobile
                    
                    # Also fetch bids / vendor requests for this service
                    bids = Bid.objects.filter(quick_service=service).select_related('vendor')
                    context['vendor_requests'] = bids
                except (ValueError, QuickService.DoesNotExist):
                    pass
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
                user_profile = u.user_profile
                user_profile.phone_number = request.POST.get('phone_number', user_profile.phone_number)
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

    elif 'profile' in path: # for user profile
        u = request.user
        context['qs_count'] = QuickService.objects.filter(user=u).count()
        context['jobs_count'] = Job.objects.filter(user=u).count()
        context['completed_qs'] = QuickService.objects.filter(user=u, status='completed').count()
        context['completed_jobs'] = Job.objects.filter(user=u, status='completed').count()
        context['vendors_selected'] = Bid.objects.filter(job__user=u, status='selected').count()
        
    if 'jobs/quotations' in path or 'quick-services/quotations' in path:
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
                'status': bid.status
            })
        context['quotations_json'] = json.dumps(bids_data)
            
    try:
        return render(request, template_name, context)
    except TemplateDoesNotExist:
        raise Http404(f"Template {template_name} not found")

def admin_dashboard(request):
    total_users = User.objects.filter(role='USER').count()
    total_vendors = VendorProfile.objects.count()
    active_jobs = Job.objects.filter(status='active').count()
    
    revenue = Subscription.objects.filter(status='success').aggregate(Sum('amount'))['amount__sum'] or 0

    recent_quick_services = QuickService.objects.order_by('-created_at')[:5]
    recent_jobs = Job.objects.order_by('-created_at')[:5]
    recent_bids = Bid.objects.order_by('-created_at')[:5]
    recent_vendors = VendorProfile.objects.order_by('-registered_date')[:5]
    recent_subscriptions = Subscription.objects.order_by('-created_at')[:5]

    context = {
        'total_users': total_users,
        'total_vendors': total_vendors,
        'active_jobs': active_jobs,
        'revenue': revenue,
        'recent_quick_services': recent_quick_services,
        'recent_jobs': recent_jobs,
        'recent_bids': recent_bids,
        'recent_vendors': recent_vendors,
        'recent_subscriptions': recent_subscriptions,
    }
    return render(request, 'admin-dashboard/dashboard.html', context)

def user_login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'ADMIN' or user.is_superuser:
                return redirect('admin_dashboard')
            elif user.role == 'VENDOR':
                return redirect('vendor_dashboard')
            elif user.role == 'USER':
                return redirect('user_dashboard')
            return redirect('admin_dashboard')
        else:
            error = 'Invalid username or password'
    return render(request, 'index.html', {'error': error})

def user_logout_view(request):
    logout(request)
    return redirect('login')

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
            
            login(request, user)
            return redirect('vendor_dashboard')

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

from datetime import datetime

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
    from .models import QuickService, Job, Bid
    from django.db.models import Sum

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
    })

    # Fetch recent items
    context['recent_quick_services'] = QuickService.objects.filter(status='open').order_by('-created_at')[:3]
    context['recent_jobs'] = Job.objects.filter(status='open').order_by('-created_at')[:2]

    return render(request, 'fixora-vendor-dashboard/dashboard.html', context)

from django.contrib.auth.decorators import login_required

@login_required
def user_dashboard(request):
    user = request.user
    
    # Active Quick Services count
    qs_list = QuickService.objects.filter(user=user)
    active_qs = qs_list.exclude(status__in=['completed', 'cancelled', 'closed']).count()
    completed_qs = qs_list.filter(status='completed').count()
    
    # Active Jobs count
    job_list = Job.objects.filter(user=user)
    active_jobs = job_list.exclude(status__in=['completed', 'cancelled', 'closed']).count()
    completed_jobs = job_list.filter(status='completed').count()
    
    # Pending Quotations count (bids on open jobs/qs)
    pending_bids_qs = Bid.objects.filter(quick_service__user=user, status='pending').count()
    pending_bids_jobs = Bid.objects.filter(job__user=user, status='pending').count()
    pending_quotations = pending_bids_qs + pending_bids_jobs
    
    # Selected Vendors count
    selected_vendors_qs = Bid.objects.filter(quick_service__user=user, status='selected').count()
    selected_vendors_jobs = Bid.objects.filter(job__user=user, status='selected').count()
    selected_vendors = selected_vendors_qs + selected_vendors_jobs
    
    # Recent items
    recent_qs = qs_list.order_by('-created_at')[:3]
    recent_jobs = job_list.order_by('-created_at')[:3]
    
    # Messages
    # In the future, we could query the Message model for recent activity.
    
    context = {
        'active_qs': active_qs,
        'active_jobs': active_jobs,
        'pending_quotations': pending_quotations,
        'selected_vendors': selected_vendors,
        'completed_qs': completed_qs,
        'completed_jobs': completed_jobs,
        'recent_qs': recent_qs,
        'recent_jobs': recent_jobs,
    }
    
    return render(request, 'user-dashboard/dashboard.html', context)

from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import UserProfile

@require_POST
def add_user_api(request):
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        mobile = data.get('mobile', '').strip()
        password = data.get('password', '').strip()

        if not name or not password:
            return JsonResponse({'success': False, 'error': 'Name and password are required.'})

        # Generate a username
        username = email if email else name.replace(" ", "").lower() + str(User.objects.count())

        # Check if username exists
        if User.objects.filter(username=username).exists():
            import random
            username = username + str(random.randint(100, 999))

        user = User.objects.create(
            username=username,
            email=email,
            role='USER',
            first_name=name
        )
        user.set_password(password)
        user.save()

        UserProfile.objects.create(user=user, phone_number=mobile)

        user_data = {
            'id': f'USR-{user.id:04d}',
            'name': name,
            'email': email or '—',
            'mobile': mobile or '—',
            'location': 'Unknown',
            'quickServices': 0,
            'jobs': 0,
            'completedJobs': 0,
            'status': 'active',
            'registered': user.date_joined.strftime('%Y-%m-%d')
        }

        return JsonResponse({'success': True, 'user': user_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def user_nav_data_api(request):
    if request.user.is_authenticated:
        u = request.user
        name = u.get_full_name() or u.username
        initials = (u.first_name[:1].upper() + u.last_name[:1].upper()) if u.first_name else u.username[:2].upper()
        return JsonResponse({'name': name, 'initials': initials})
    return JsonResponse({'name': 'Guest', 'initials': 'GU'})

@require_POST
def add_category_api(request):
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        service_type = data.get('service_type', 'both')
        status = data.get('status', 'active')

        if not name:
            return JsonResponse({'success': False, 'error': 'Name is required.'})

        cat = Category.objects.create(
            name=name,
            service_type=service_type,
            status=status
        )

        cat_data = {
            'id': cat.id,
            'name': cat.name,
            'service_type': cat.service_type,
            'status': cat.status,
            'created_at': cat.created_at.strftime('%Y-%m-%d')
        }

        return JsonResponse({'success': True, 'category': cat_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
def update_category_api(request):
    try:
        data = json.loads(request.body)
        cat_id = data.get('id')
        name = data.get('name', '').strip()
        service_type = data.get('service_type', 'both')
        status = data.get('status', 'active')

        if not cat_id or not name:
            return JsonResponse({'success': False, 'error': 'ID and Name are required.'})

        cat = Category.objects.get(id=cat_id)
        cat.name = name
        cat.service_type = service_type
        cat.status = status
        cat.save()

        cat_data = {
            'id': cat.id,
            'name': cat.name,
            'service_type': cat.service_type,
            'status': cat.status,
            'created_at': cat.created_at.strftime('%Y-%m-%d')
        }

        return JsonResponse({'success': True, 'category': cat_data})
    except Category.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Category not found.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
def delete_category_api(request):
    try:
        data = json.loads(request.body)
        cat_id = data.get('id')

        if not cat_id:
            return JsonResponse({'success': False, 'error': 'ID is required.'})

        cat = Category.objects.get(id=cat_id)
        cat.delete()

        return JsonResponse({'success': True})
    except Category.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Category not found.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

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

