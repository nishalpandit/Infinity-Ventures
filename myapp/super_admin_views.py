from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import (
    CustomUser, VendorProfile, UserProfile, Job, QuickService, 
    Category, GlobalSettings, Location, Bid, Subscription, Message,
    SiteBranding, HeroSection, QuickServiceCard, FeaturedProjectCard,
    PackageCard, Testimonial, TrustMetric
)
from .cms_forms import (
    SiteBrandingForm, HeroSectionForm, QuickServiceCardForm,
    FeaturedProjectCardForm, PackageCardForm, TestimonialForm,
    TrustMetricForm
)

LOGIN_URL = '/super-admin/login/'

def super_admin_check(user):
    return user.is_authenticated and user.is_superuser

def sa_required(view_func):
    """Decorator combining login_required + superuser check."""
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'{LOGIN_URL}?next={request.path}')
        if not request.user.is_superuser:
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return wrapper

# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────
def super_admin_login_view(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('/super-admin/')
    error = None
    next_url = request.GET.get('next', '/super-admin/')
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        next_val = request.POST.get('next', '/super-admin/')
        user = authenticate(request, username=u, password=p)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect(next_val)
        else:
            error = "Invalid credentials or insufficient privileges."
    return render(request, 'superadmin/login.html', {'error': error, 'next': next_url})

# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────
@sa_required
def super_admin_dashboard(request):
    total_users = CustomUser.objects.filter(role='USER').count()
    total_vendors = VendorProfile.objects.count()
    total_admins = CustomUser.objects.filter(role='ADMIN').count()
    active_jobs = Job.objects.filter(status__in=['open', 'progress']).count()
    total_jobs = Job.objects.count()
    total_qs = QuickService.objects.count()
    total_bids = Bid.objects.count()
    total_categories = Category.objects.count()
    total_locations = Location.objects.count()
    settings_obj = GlobalSettings.objects.first()

    context = {
        'total_users': total_users,
        'total_vendors': total_vendors,
        'total_admins': total_admins,
        'active_jobs': active_jobs,
        'total_jobs': total_jobs,
        'total_qs': total_qs,
        'total_bids': total_bids,
        'total_categories': total_categories,
        'total_locations': total_locations,
        'settings': settings_obj,
    }
    return render(request, 'superadmin/dashboard.html', context)

from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# ─────────────────────────────────────────────
# USERS  (List + Filter + Paginate + Create + Edit + Delete + Toggle)
# ─────────────────────────────────────────────
@sa_required
def super_admin_users(request):
    q = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', '').strip()
    state_filter = request.GET.get('state', '').strip()
    status_filter = request.GET.get('status', '').strip()
    sort = request.GET.get('sort', 'newest').strip()
    page = request.GET.get('page', 1)

    users_qs = CustomUser.objects.all().select_related('user_profile', 'vendor_profile')

    # 1. Search Query (q)
    if q:
        users_qs = users_qs.filter(
            Q(username__icontains=q) |
            Q(email__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(assigned_state__icontains=q) |
            Q(user_profile__phone_number__icontains=q) |
            Q(vendor_profile__company_name__icontains=q) |
            Q(vendor_profile__location__icontains=q)
        ).distinct()

    # 2. Role Filter
    if role_filter and role_filter != 'all':
        if role_filter == 'superuser':
            users_qs = users_qs.filter(is_superuser=True)
        elif role_filter == 'ADMIN':
            users_qs = users_qs.filter(role='ADMIN', is_superuser=False)
        elif role_filter == 'USER':
            users_qs = users_qs.filter(role='USER')
        elif role_filter == 'VENDOR':
            users_qs = users_qs.filter(role='VENDOR')

    # 3. State / Territory Filter
    if state_filter and state_filter != 'all':
        users_qs = users_qs.filter(
            Q(assigned_state__iexact=state_filter) |
            Q(vendor_profile__location__icontains=state_filter)
        ).distinct()

    # 4. Status Filter (Active / Disabled)
    if status_filter and status_filter != 'all':
        if status_filter == 'active':
            users_qs = users_qs.filter(is_active=True)
        elif status_filter == 'inactive':
            users_qs = users_qs.filter(is_active=False)

    # 5. Sorting
    if sort == 'oldest':
        users_qs = users_qs.order_by('date_joined')
    elif sort == 'name_asc':
        users_qs = users_qs.order_by('username')
    elif sort == 'name_desc':
        users_qs = users_qs.order_by('-username')
    else:  # newest
        users_qs = users_qs.order_by('-date_joined')

    # Total matching count before pagination
    total_matching_users = users_qs.count()

    # Available states for territory dropdown
    active_states = list(Location.objects.values_list('state', flat=True).distinct().order_by('state'))
    default_states = ['Jharkhand', 'Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'Uttar Pradesh', 'West Bengal', 'Gujarat', 'Bihar', 'Rajasthan', 'Madhya Pradesh', 'Telangana', 'Andhra Pradesh', 'Kerala', 'Punjab', 'Haryana', 'Odisha']
    states = sorted(list(set([s for s in (active_states + default_states) if s])))

    # Pagination (10 users per page)
    paginator = Paginator(users_qs, 10)
    try:
        users = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        users = paginator.page(1)

    # Construct extra query string for pagination links (preserves all filters)
    get_copy = request.GET.copy()
    if 'page' in get_copy:
        del get_copy['page']
    extra_query_params = get_copy.urlencode()

    # Quick overview counters
    all_count = CustomUser.objects.count()
    admin_count = CustomUser.objects.filter(role='ADMIN', is_superuser=False).count()
    customer_count = CustomUser.objects.filter(role='USER').count()
    vendor_count = CustomUser.objects.filter(role='VENDOR').count()

    # Check if any active filters are applied
    has_active_filters = bool(q or (role_filter and role_filter != 'all') or (state_filter and state_filter != 'all') or (status_filter and status_filter != 'all') or (sort and sort != 'newest'))

    # Elided page range for pagination controls
    page_range = paginator.get_elided_page_range(users.number, on_each_side=2, on_ends=1)

    context = {
        'users': users,
        'page_range': page_range,
        'q': q,
        'role_filter': role_filter,
        'state_filter': state_filter,
        'status_filter': status_filter,
        'sort': sort,
        'states': states,
        'total_matching_users': total_matching_users,
        'all_count': all_count,
        'admin_count': admin_count,
        'customer_count': customer_count,
        'vendor_count': vendor_count,
        'extra_query_params': extra_query_params,
        'has_active_filters': has_active_filters,
    }
    return render(request, 'superadmin/user_manager.html', context)

@sa_required
def super_admin_user_create(request):
    active_states = list(Location.objects.values_list('state', flat=True).distinct().order_by('state'))
    default_states = ['Jharkhand', 'Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'Uttar Pradesh', 'West Bengal', 'Gujarat', 'Bihar', 'Rajasthan', 'Madhya Pradesh', 'Telangana', 'Andhra Pradesh', 'Kerala', 'Punjab', 'Haryana', 'Odisha']
    states = sorted(list(set([s for s in (active_states + default_states) if s])))

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email', '')
        password = request.POST.get('password')
        role = request.POST.get('role', 'USER')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        assigned_state = request.POST.get('assigned_state', '').strip()
        
        if CustomUser.objects.filter(username=username).exists():
            django_messages.error(request, f'Username "{username}" already exists.')
            return redirect('super_admin_user_create')
        
        user = CustomUser.objects.create_user(
            username=username, email=email, password=password,
            role=role, first_name=first_name, last_name=last_name
        )
        user.assigned_state = assigned_state
        if role == 'ADMIN':
            user.is_staff = True
        user.save()
        django_messages.success(request, f'User "{username}" created successfully.')
        return redirect('super_admin_users')
    return render(request, 'superadmin/user_form.html', {'mode': 'create', 'states': states})

@sa_required
def super_admin_user_edit(request, user_id):
    user_obj = get_object_or_404(CustomUser, pk=user_id)
    active_states = list(Location.objects.values_list('state', flat=True).distinct().order_by('state'))
    default_states = ['Jharkhand', 'Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'Uttar Pradesh', 'West Bengal', 'Gujarat', 'Bihar', 'Rajasthan', 'Madhya Pradesh', 'Telangana', 'Andhra Pradesh', 'Kerala', 'Punjab', 'Haryana', 'Odisha']
    states = sorted(list(set([s for s in (active_states + default_states) if s])))

    if request.method == 'POST':
        user_obj.first_name = request.POST.get('first_name', '')
        user_obj.last_name = request.POST.get('last_name', '')
        user_obj.email = request.POST.get('email', '')
        user_obj.role = request.POST.get('role', user_obj.role)
        user_obj.assigned_state = request.POST.get('assigned_state', '').strip()
        user_obj.is_active = request.POST.get('is_active') == 'on'
        new_pass = request.POST.get('password', '')
        if new_pass:
            user_obj.set_password(new_pass)
        if user_obj.role == 'ADMIN':
            user_obj.is_staff = True
        user_obj.save()
        django_messages.success(request, f'User "{user_obj.username}" updated.')
        return redirect('super_admin_users')
    return render(request, 'superadmin/user_form.html', {'mode': 'edit', 'user_obj': user_obj, 'states': states})

@sa_required
def super_admin_user_delete(request, user_id):
    user_obj = get_object_or_404(CustomUser, pk=user_id)
    if user_obj == request.user:
        django_messages.error(request, "You cannot delete yourself.")
        return redirect('super_admin_users')
    username = user_obj.username
    user_obj.delete()
    django_messages.success(request, f'User "{username}" deleted.')
    return redirect('super_admin_users')

@sa_required
def super_admin_user_toggle(request, user_id):
    user_obj = get_object_or_404(CustomUser, pk=user_id)
    user_obj.is_active = not user_obj.is_active
    user_obj.save()
    status = "activated" if user_obj.is_active else "deactivated"
    django_messages.success(request, f'User "{user_obj.username}" {status}.')
    return redirect('super_admin_users')

# ─────────────────────────────────────────────
# VENDORS (List + Create + Edit + Delete + Toggle)
# ─────────────────────────────────────────────
@sa_required
def super_admin_vendors(request):
    vendors_qs = VendorProfile.objects.all().select_related('user').order_by('-registered_date')
    paginator = Paginator(vendors_qs, 10)
    page_num = request.GET.get('page', 1)
    try:
        vendors = paginator.page(page_num)
    except (EmptyPage, PageNotAnInteger):
        vendors = paginator.page(1)
    page_range = paginator.get_elided_page_range(vendors.number, on_each_side=2, on_ends=1)
    return render(request, 'superadmin/vendors.html', {'vendors': vendors, 'page_range': page_range})

@sa_required
def super_admin_vendor_create(request):
    active_states = list(Location.objects.values_list('state', flat=True).distinct().order_by('state'))
    default_states = ['Jharkhand', 'Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'Uttar Pradesh', 'West Bengal', 'Gujarat', 'Bihar', 'Rajasthan', 'Madhya Pradesh', 'Telangana', 'Andhra Pradesh', 'Kerala', 'Punjab', 'Haryana', 'Odisha']
    states = sorted(list(set([s for s in (active_states + default_states) if s])))
    categories = Category.objects.all().order_by('name')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        company_name = request.POST.get('company_name', '').strip()
        vendor_type = request.POST.get('vendor_type', 'vendor')
        category = request.POST.get('category', '').strip()
        state = request.POST.get('state', '').strip()
        city = request.POST.get('city', '').strip()
        location = f"{city}, {state}".strip(', ') if (city or state) else request.POST.get('location', '').strip()
        experience = request.POST.get('experience', 0) or 0
        rating = request.POST.get('rating', 5.0) or 5.0
        about = request.POST.get('about', '').strip()

        if not username:
            username = email if email else company_name.replace(" ", "").lower() + str(CustomUser.objects.count())

        if CustomUser.objects.filter(username=username).exists():
            django_messages.error(request, f'Username "{username}" is already taken.')
            return redirect('super_admin_vendor_create')

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='VENDOR',
            first_name=company_name
        )
        user.assigned_state = state
        user.save()

        VendorProfile.objects.create(
            user=user,
            vendor_type=vendor_type,
            company_name=company_name,
            category=category,
            location=location,
            experience=experience,
            rating=rating,
            about=about
        )
        django_messages.success(request, f'Vendor "{company_name or username}" created successfully.')
        return redirect('super_admin_vendors')

    return render(request, 'superadmin/vendor_form.html', {
        'mode': 'create',
        'states': states,
        'categories': categories
    })

@sa_required
def super_admin_vendor_edit(request, vendor_id):
    vendor = get_object_or_404(VendorProfile, pk=vendor_id)
    categories = Category.objects.all().order_by('name')
    if request.method == 'POST':
        vendor.company_name = request.POST.get('company_name', '')
        vendor.category = request.POST.get('category', '')
        vendor.location = request.POST.get('location', '')
        vendor.vendor_type = request.POST.get('vendor_type', 'vendor')
        vendor.experience = request.POST.get('experience', 0) or 0
        vendor.about = request.POST.get('about', '')
        vendor.rating = request.POST.get('rating', 0) or 0
        vendor.save()
        django_messages.success(request, f'Vendor "{vendor}" updated.')
        return redirect('super_admin_vendors')
    return render(request, 'superadmin/vendor_form.html', {'mode': 'edit', 'vendor': vendor, 'categories': categories})

@sa_required
def super_admin_vendor_delete(request, vendor_id):
    vendor = get_object_or_404(VendorProfile, pk=vendor_id)
    name = str(vendor)
    vendor.user.delete()  # cascade deletes the vendor profile too
    django_messages.success(request, f'Vendor "{name}" and their account deleted.')
    return redirect('super_admin_vendors')

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# ─────────────────────────────────────────────
# CMS: CATEGORIES (List + Create + Edit + Delete)
# ─────────────────────────────────────────────
@sa_required
def super_admin_cms(request):
    cat_queryset = Category.objects.all().order_by('-created_at')
    loc_queryset = Location.objects.all().order_by('-created_at')
    
    # 8 per page for categories
    cat_paginator = Paginator(cat_queryset, 8)
    cat_page = request.GET.get('cat_page', 1)
    try:
        categories = cat_paginator.page(cat_page)
    except (EmptyPage, PageNotAnInteger):
        categories = cat_paginator.page(1)
        
    # 8 per page for locations
    loc_paginator = Paginator(loc_queryset, 8)
    loc_page = request.GET.get('loc_page', 1)
    try:
        locations = loc_paginator.page(loc_page)
    except (EmptyPage, PageNotAnInteger):
        locations = loc_paginator.page(1)

    return render(request, 'superadmin/cms_manager.html', {
        'categories': categories,
        'locations': locations,
        'cat_page': categories.number,
        'loc_page': locations.number,
        'total_categories': cat_queryset.count(),
        'total_locations': loc_queryset.count(),
    })

@sa_required
def super_admin_category_create(request):
    if request.method == 'POST':
        Category.objects.create(
            name=request.POST.get('name'),
            service_type=request.POST.get('service_type', 'both'),
            status=request.POST.get('status', 'active'),
        )
        django_messages.success(request, 'Category created.')
        return redirect('super_admin_cms')
    return render(request, 'superadmin/category_form.html', {'mode': 'create'})

@sa_required
def super_admin_category_edit(request, cat_id):
    cat = get_object_or_404(Category, pk=cat_id)
    if request.method == 'POST':
        cat.name = request.POST.get('name', cat.name)
        cat.service_type = request.POST.get('service_type', cat.service_type)
        cat.status = request.POST.get('status', cat.status)
        cat.save()
        django_messages.success(request, f'Category "{cat.name}" updated.')
        return redirect('super_admin_cms')
    return render(request, 'superadmin/category_form.html', {'mode': 'edit', 'cat': cat})

@sa_required
def super_admin_category_delete(request, cat_id):
    cat = get_object_or_404(Category, pk=cat_id)
    cat.delete()
    django_messages.success(request, 'Category deleted.')
    return redirect('super_admin_cms')

# ─────────────────────────────────────────────
# CMS: LOCATIONS (Create + Edit + Delete)
# ─────────────────────────────────────────────
@sa_required
def super_admin_location_create(request):
    if request.method == 'POST':
        Location.objects.create(
            state=request.POST.get('state'),
            city=request.POST.get('city'),
            status=request.POST.get('status', 'active'),
        )
        django_messages.success(request, 'Location created.')
        return redirect('super_admin_cms')
    return render(request, 'superadmin/location_form.html', {'mode': 'create'})

@sa_required
def super_admin_location_edit(request, loc_id):
    loc = get_object_or_404(Location, pk=loc_id)
    if request.method == 'POST':
        loc.state = request.POST.get('state', loc.state)
        loc.city = request.POST.get('city', loc.city)
        loc.status = request.POST.get('status', loc.status)
        loc.save()
        django_messages.success(request, f'Location "{loc}" updated.')
        return redirect('super_admin_cms')
    return render(request, 'superadmin/location_form.html', {'mode': 'edit', 'loc': loc})

@sa_required
def super_admin_location_delete(request, loc_id):
    loc = get_object_or_404(Location, pk=loc_id)
    loc.delete()
    django_messages.success(request, 'Location deleted.')
    return redirect('super_admin_cms')

# ─────────────────────────────────────────────
# JOBS (List + Create + Edit + Delete + Bids Management & Vendor Assignment)
# ─────────────────────────────────────────────
@sa_required
def super_admin_jobs(request):
    jobs_qs = Job.objects.all().select_related('user', 'category', 'location', 'assigned_vendor').prefetch_related('bids').order_by('-created_at')
    paginator = Paginator(jobs_qs, 10)
    page_num = request.GET.get('page', 1)
    try:
        jobs = paginator.page(page_num)
    except (EmptyPage, PageNotAnInteger):
        jobs = paginator.page(1)
    page_range = paginator.get_elided_page_range(jobs.number, on_each_side=2, on_ends=1)
    return render(request, 'superadmin/jobs.html', {'jobs': jobs, 'page_range': page_range})

@sa_required
def super_admin_job_create(request):
    users = CustomUser.objects.filter(role='USER').order_by('username')
    vendors = CustomUser.objects.filter(role='VENDOR').select_related('vendor_profile').order_by('username')
    categories = Category.objects.all().order_by('name')
    locations = Location.objects.all().order_by('state', 'city')

    if request.method == 'POST':
        user_id = request.POST.get('user')
        title = request.POST.get('title', '').strip()
        cat_id = request.POST.get('category')
        loc_id = request.POST.get('location')
        budget = request.POST.get('budget', 0) or 0
        max_bids = request.POST.get('max_bids')
        min_bid_amount = request.POST.get('min_bid_amount')
        max_bid_amount = request.POST.get('max_bid_amount')
        assigned_vendor_id = request.POST.get('assigned_vendor')
        status = request.POST.get('status', 'open')
        description = request.POST.get('description', '').strip()
        address = request.POST.get('address', '').strip()

        customer = get_object_or_404(CustomUser, pk=user_id)
        cat_obj = Category.objects.filter(id=cat_id).first() if cat_id else None
        loc_obj = Location.objects.filter(id=loc_id).first() if loc_id else None
        assigned_v = CustomUser.objects.filter(id=assigned_vendor_id, role='VENDOR').first() if assigned_vendor_id else None

        job = Job.objects.create(
            user=customer,
            title=title,
            category=cat_obj,
            location=loc_obj,
            budget=budget,
            max_bids=int(max_bids) if max_bids else 10,
            min_bid_amount=float(min_bid_amount) if min_bid_amount else None,
            max_bid_amount=float(max_bid_amount) if max_bid_amount else None,
            assigned_vendor=assigned_v,
            status=status if not assigned_v else ('selected' if status == 'open' else status),
            description=description,
            address=address,
            contact_name=customer.get_full_name() or customer.username
        )
        django_messages.success(request, f'Job "{job.title}" created successfully.')
        return redirect('super_admin_jobs')

    return render(request, 'superadmin/job_form.html', {
        'mode': 'create',
        'users': users,
        'vendors': vendors,
        'categories': categories,
        'locations': locations
    })

@sa_required
def super_admin_job_edit(request, job_id):
    job = get_object_or_404(Job.objects.select_related('assigned_vendor'), pk=job_id)
    categories = Category.objects.all().order_by('name')
    locations = Location.objects.all().order_by('state', 'city')
    users = CustomUser.objects.filter(role='USER').order_by('username')
    vendors = CustomUser.objects.filter(role='VENDOR').select_related('vendor_profile').order_by('username')
    
    if request.method == 'POST':
        job.title = request.POST.get('title', job.title)
        job.status = request.POST.get('status', job.status)
        job.budget = request.POST.get('budget', job.budget)
        
        max_bids = request.POST.get('max_bids')
        job.max_bids = int(max_bids) if max_bids else None
        
        min_bid_amount = request.POST.get('min_bid_amount')
        job.min_bid_amount = float(min_bid_amount) if min_bid_amount else None
        
        max_bid_amount = request.POST.get('max_bid_amount')
        job.max_bid_amount = float(max_bid_amount) if max_bid_amount else None
        
        assigned_vendor_id = request.POST.get('assigned_vendor')
        if assigned_vendor_id:
            job.assigned_vendor = CustomUser.objects.filter(id=assigned_vendor_id, role='VENDOR').first()
            if job.status == 'open':
                job.status = 'selected'
        else:
            job.assigned_vendor = None

        cat_id = request.POST.get('category')
        if cat_id:
            job.category = get_object_or_404(Category, pk=cat_id)
        loc_id = request.POST.get('location')
        if loc_id:
            job.location = Location.objects.filter(id=loc_id).first()
        job.description = request.POST.get('description', job.description)
        job.save()
        django_messages.success(request, f'Job "{job.title}" updated.')
        return redirect('super_admin_jobs')
    return render(request, 'superadmin/job_form.html', {
        'mode': 'edit',
        'job': job,
        'categories': categories,
        'locations': locations,
        'users': users,
        'vendors': vendors
    })

@sa_required
def super_admin_job_delete(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    job.delete()
    django_messages.success(request, 'Job deleted.')
    return redirect('super_admin_jobs')

@sa_required
def super_admin_job_bids(request, job_id):
    """
    Dedicated view for Super Admin to:
    1. See all vendor bids submitted for this job.
    2. Manage bidding limit (max_bids) and pricing boundaries (min_bid_amount, max_bid_amount, budget).
    3. Assign/Select a vendor directly or select from submitted bids.
    4. Create a manual bid on behalf of a vendor.
    """
    job = get_object_or_404(
        Job.objects.select_related('user', 'category', 'location', 'assigned_vendor'),
        pk=job_id
    )
    vendors = CustomUser.objects.filter(role='VENDOR').select_related('vendor_profile').order_by('username')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_limits':
            max_bids_val = request.POST.get('max_bids', '').strip()
            min_bid_val = request.POST.get('min_bid_amount', '').strip()
            max_bid_val = request.POST.get('max_bid_amount', '').strip()
            budget_val = request.POST.get('budget', '').strip()
            status_val = request.POST.get('status', '').strip()

            if max_bids_val:
                try:
                    job.max_bids = max(1, int(max_bids_val))
                except (ValueError, TypeError):
                    pass
            else:
                job.max_bids = None

            if min_bid_val:
                try:
                    job.min_bid_amount = float(min_bid_val)
                except (ValueError, TypeError):
                    pass
            else:
                job.min_bid_amount = None

            if max_bid_val:
                try:
                    job.max_bid_amount = float(max_bid_val)
                except (ValueError, TypeError):
                    pass
            else:
                job.max_bid_amount = None

            if budget_val:
                try:
                    job.budget = float(budget_val)
                except (ValueError, TypeError):
                    pass

            if status_val:
                job.status = status_val

            job.save()
            django_messages.success(request, 'Bidding parameters & limits updated successfully.')
            return redirect('super_admin_job_bids', job_id=job.id)

        elif action == 'assign_vendor':
            vendor_id = request.POST.get('vendor_id')
            if vendor_id:
                vendor = get_object_or_404(CustomUser, pk=vendor_id, role='VENDOR')
                job.assigned_vendor = vendor
                if job.status in ['open', 'cancelled']:
                    job.status = 'selected'
                job.save()
                # Mark existing bid if any as selected
                Bid.objects.filter(job=job, vendor=vendor).update(status='selected')
                django_messages.success(request, f'Vendor "{vendor.get_full_name() or vendor.username}" assigned to Job #{job.id}.')
            else:
                job.assigned_vendor = None
                job.save()
                django_messages.success(request, 'Vendor assignment removed.')
            return redirect('super_admin_job_bids', job_id=job.id)

        elif action == 'select_bid':
            bid_id = request.POST.get('bid_id')
            bid = get_object_or_404(Bid, pk=bid_id, job=job)
            Bid.objects.filter(job=job).exclude(id=bid.id).filter(status='selected').update(status='submitted')
            bid.status = 'selected'
            bid.save()
            job.assigned_vendor = bid.vendor
            job.status = 'selected'
            job.save()
            django_messages.success(request, f'Bid from "{bid.vendor.username}" for ₹{bid.amount} accepted & vendor assigned!')
            return redirect('super_admin_job_bids', job_id=job.id)

        elif action == 'reject_bid':
            bid_id = request.POST.get('bid_id')
            bid = get_object_or_404(Bid, pk=bid_id, job=job)
            bid.status = 'rejected'
            bid.save()
            if job.assigned_vendor == bid.vendor:
                job.assigned_vendor = None
                job.status = 'open'
                job.save()
            django_messages.success(request, f'Bid from "{bid.vendor.username}" rejected.')
            return redirect('super_admin_job_bids', job_id=job.id)

        elif action == 'delete_bid':
            bid_id = request.POST.get('bid_id')
            bid = get_object_or_404(Bid, pk=bid_id, job=job)
            if job.assigned_vendor == bid.vendor:
                job.assigned_vendor = None
                job.save()
            bid.delete()
            django_messages.success(request, 'Bid deleted successfully.')
            return redirect('super_admin_job_bids', job_id=job.id)

        elif action == 'create_bid':
            vendor_id = request.POST.get('vendor_id')
            amount = request.POST.get('amount')
            estimated_time = request.POST.get('estimated_time', '').strip()
            proposal = request.POST.get('proposal', '').strip()
            status_bid = request.POST.get('bid_status', 'submitted')

            if vendor_id and amount:
                vendor = get_object_or_404(CustomUser, pk=vendor_id, role='VENDOR')
                if job.max_bids and job.bids.count() >= job.max_bids:
                    django_messages.error(request, f'Job has reached the maximum limit of {job.max_bids} bids.')
                    return redirect('super_admin_job_bids', job_id=job.id)

                bid = Bid.objects.create(
                    vendor=vendor,
                    job=job,
                    amount=amount,
                    estimated_time=estimated_time,
                    proposal=proposal,
                    status=status_bid
                )
                if status_bid == 'selected':
                    job.assigned_vendor = vendor
                    job.status = 'selected'
                    job.save()
                django_messages.success(request, f'Bid of ₹{bid.amount} recorded for {vendor.username}.')
            return redirect('super_admin_job_bids', job_id=job.id)

    bids = job.bids.all().select_related('vendor', 'vendor__vendor_profile').order_by('-created_at')
    bids_count = bids.count()
    is_limit_reached = bool(job.max_bids and bids_count >= job.max_bids)

    context = {
        'job': job,
        'bids': bids,
        'bids_count': bids_count,
        'is_limit_reached': is_limit_reached,
        'vendors': vendors,
    }
    return render(request, 'superadmin/job_bids.html', context)

# ─────────────────────────────────────────────
# QUICK SERVICES (List + Create + Edit + Delete)
# ─────────────────────────────────────────────
@sa_required
def super_admin_quick_services(request):
    qs_list = QuickService.objects.all().select_related('user', 'category', 'location').order_by('-created_at')
    paginator = Paginator(qs_list, 10)
    page_num = request.GET.get('page', 1)
    try:
        qservices = paginator.page(page_num)
    except (EmptyPage, PageNotAnInteger):
        qservices = paginator.page(1)
    page_range = paginator.get_elided_page_range(qservices.number, on_each_side=2, on_ends=1)
    return render(request, 'superadmin/quick_services.html', {'qservices': qservices, 'page_range': page_range})

@sa_required
def super_admin_qs_create(request):
    users = CustomUser.objects.filter(role='USER').order_by('username')
    categories = Category.objects.all().order_by('name')
    locations = Location.objects.all().order_by('state', 'city')

    if request.method == 'POST':
        user_id = request.POST.get('user')
        title = request.POST.get('title', '').strip()
        cat_id = request.POST.get('category')
        loc_id = request.POST.get('location')
        budget = request.POST.get('budget', 0) or 0
        status = request.POST.get('status', 'open')
        description = request.POST.get('description', '').strip()
        address = request.POST.get('address', '').strip()

        customer = get_object_or_404(CustomUser, pk=user_id)
        cat_obj = Category.objects.filter(id=cat_id).first() if cat_id else None
        loc_obj = Location.objects.filter(id=loc_id).first() if loc_id else None

        qs = QuickService.objects.create(
            user=customer,
            title=title,
            category=cat_obj,
            location=loc_obj,
            budget=budget,
            status=status,
            description=description,
            address=address,
            contact_name=customer.get_full_name() or customer.username
        )
        django_messages.success(request, f'Quick Service "{qs.title}" created successfully.')
        return redirect('super_admin_quick_services')

    return render(request, 'superadmin/qs_form.html', {
        'mode': 'create',
        'users': users,
        'categories': categories,
        'locations': locations
    })

@sa_required
def super_admin_qs_edit(request, qs_id):
    qs = get_object_or_404(QuickService, pk=qs_id)
    categories = Category.objects.all()
    locations = Location.objects.all().order_by('state', 'city')
    users = CustomUser.objects.filter(role='USER').order_by('username')
    if request.method == 'POST':
        qs.title = request.POST.get('title', qs.title)
        qs.status = request.POST.get('status', qs.status)
        qs.budget = request.POST.get('budget', qs.budget)
        cat_id = request.POST.get('category')
        if cat_id:
            qs.category = get_object_or_404(Category, pk=cat_id)
        loc_id = request.POST.get('location')
        if loc_id:
            qs.location = Location.objects.filter(id=loc_id).first()
        qs.description = request.POST.get('description', qs.description)
        qs.save()
        django_messages.success(request, f'Quick Service "{qs.title}" updated.')
        return redirect('super_admin_quick_services')
    return render(request, 'superadmin/qs_form.html', {'mode': 'edit', 'qs': qs, 'categories': categories, 'locations': locations, 'users': users})

@sa_required
def super_admin_qs_delete(request, qs_id):
    qs = get_object_or_404(QuickService, pk=qs_id)
    qs.delete()
    django_messages.success(request, 'Quick Service deleted.')
    return redirect('super_admin_quick_services')

# ─────────────────────────────────────────────
# BIDS (List + Create + Edit + Delete)
# ─────────────────────────────────────────────
@sa_required
def super_admin_bids(request):
    bids_qs = Bid.objects.all().select_related('vendor', 'job', 'quick_service').order_by('-created_at')
    paginator = Paginator(bids_qs, 10)
    page_num = request.GET.get('page', 1)
    try:
        bids = paginator.page(page_num)
    except (EmptyPage, PageNotAnInteger):
        bids = paginator.page(1)
    page_range = paginator.get_elided_page_range(bids.number, on_each_side=2, on_ends=1)
    return render(request, 'superadmin/bids.html', {'bids': bids, 'page_range': page_range})

@sa_required
def super_admin_bid_create(request):
    vendors = CustomUser.objects.filter(role='VENDOR').order_by('username')
    jobs = Job.objects.filter(status__in=['open', 'progress']).order_by('-created_at')
    qservices = QuickService.objects.filter(status__in=['open', 'progress']).order_by('-created_at')

    if request.method == 'POST':
        vendor_id = request.POST.get('vendor')
        target_type = request.POST.get('target_type', 'job')
        target_id = request.POST.get('target_id')
        amount = request.POST.get('amount', 0) or 0
        status = request.POST.get('status', 'pending')
        proposal = request.POST.get('proposal', '').strip()

        vendor = get_object_or_404(CustomUser, pk=vendor_id)
        job_obj = None
        qs_obj = None

        if target_type == 'job' and target_id:
            job_obj = get_object_or_404(Job, pk=target_id)
        elif target_type == 'quick_service' and target_id:
            qs_obj = get_object_or_404(QuickService, pk=target_id)

        bid = Bid.objects.create(
            vendor=vendor,
            job=job_obj,
            quick_service=qs_obj,
            amount=amount,
            status=status,
            proposal=proposal
        )
        django_messages.success(request, f'Bid of ₹{bid.amount} created successfully for {vendor.username}.')
        return redirect('super_admin_bids')

    return render(request, 'superadmin/bid_form.html', {
        'mode': 'create',
        'vendors': vendors,
        'jobs': jobs,
        'qservices': qservices
    })

@sa_required
def super_admin_bid_edit(request, bid_id):
    bid = get_object_or_404(Bid, pk=bid_id)
    if request.method == 'POST':
        bid.status = request.POST.get('status', bid.status)
        bid.amount = request.POST.get('amount', bid.amount)
        bid.save()
        django_messages.success(request, 'Bid updated.')
        return redirect('super_admin_bids')
    return render(request, 'superadmin/bid_form.html', {'mode': 'edit', 'bid': bid})

@sa_required
def super_admin_bid_delete(request, bid_id):
    bid = get_object_or_404(Bid, pk=bid_id)
    bid.delete()
    django_messages.success(request, 'Bid deleted.')
    return redirect('super_admin_bids')

# ─────────────────────────────────────────────
# SUBSCRIPTIONS (List + Create + Delete)
# ─────────────────────────────────────────────
@sa_required
def super_admin_subscriptions(request):
    subscriptions_qs = Subscription.objects.all().select_related('vendor').order_by('-created_at')
    paginator = Paginator(subscriptions_qs, 10)
    page_num = request.GET.get('page', 1)
    try:
        subscriptions = paginator.page(page_num)
    except (EmptyPage, PageNotAnInteger):
        subscriptions = paginator.page(1)
    page_range = paginator.get_elided_page_range(subscriptions.number, on_each_side=2, on_ends=1)
    return render(request, 'superadmin/subscriptions.html', {'subscriptions': subscriptions, 'page_range': page_range})

@sa_required
def super_admin_subscription_create(request):
    vendors = CustomUser.objects.filter(role='VENDOR').order_by('username')
    if request.method == 'POST':
        vendor_id = request.POST.get('vendor')
        package_name = request.POST.get('package_name', 'Pro Growth Tier')
        amount = request.POST.get('amount', 0) or 0
        status = request.POST.get('status', 'success')
        credits = int(request.POST.get('credits', 50) or 50)

        vendor = get_object_or_404(CustomUser, pk=vendor_id)
        sub = Subscription.objects.create(
            vendor=vendor,
            package_name=package_name,
            amount=amount,
            status=status
        )

        # Update vendor profile credits if success
        if status == 'success' and hasattr(vendor, 'vendor_profile'):
            vp = vendor.vendor_profile
            vp.bid_credits = getattr(vp, 'bid_credits', 0) + credits
            vp.save()

        django_messages.success(request, f'Subscription of ₹{sub.amount} added for {vendor.username}.')
        return redirect('super_admin_subscriptions')

    return render(request, 'superadmin/subscription_form.html', {
        'mode': 'create',
        'vendors': vendors
    })

@sa_required
def super_admin_subscription_delete(request, sub_id):
    sub = get_object_or_404(Subscription, pk=sub_id)
    sub.delete()
    django_messages.success(request, 'Subscription deleted.')
    return redirect('super_admin_subscriptions')

# ─────────────────────────────────────────────
# MESSAGES (List + Delete)
# ─────────────────────────────────────────────
@sa_required
def super_admin_messages(request):
    msgs_qs = Message.objects.all().select_related('sender', 'receiver').order_by('-created_at')
    paginator = Paginator(msgs_qs, 10)
    page_num = request.GET.get('page', 1)
    try:
        msgs = paginator.page(page_num)
    except (EmptyPage, PageNotAnInteger):
        msgs = paginator.page(1)
    page_range = paginator.get_elided_page_range(msgs.number, on_each_side=2, on_ends=1)
    return render(request, 'superadmin/messages.html', {'chat_messages': msgs, 'page_range': page_range})

@sa_required
def super_admin_message_delete(request, msg_id):
    msg = get_object_or_404(Message, pk=msg_id)
    msg.delete()
    django_messages.success(request, 'Message deleted.')
    return redirect('super_admin_messages')

# ─────────────────────────────────────────────
# GLOBAL SETTINGS (Edit)
# ─────────────────────────────────────────────
@sa_required
def super_admin_settings(request):
    settings_obj, _ = GlobalSettings.objects.get_or_create(pk=1)
    if request.method == 'POST':
        settings_obj.site_title = request.POST.get('site_title', settings_obj.site_title)
        settings_obj.contact_email = request.POST.get('contact_email', settings_obj.contact_email)
        settings_obj.support_phone = request.POST.get('support_phone', settings_obj.support_phone)
        settings_obj.maintenance_mode = request.POST.get('maintenance_mode') == 'on'
        settings_obj.platform_commission_percent = request.POST.get('platform_commission_percent', settings_obj.platform_commission_percent)
        settings_obj.save()
        django_messages.success(request, 'Global settings saved.')
        return redirect('super_admin_settings')
    return render(request, 'superadmin/settings.html', {'settings': settings_obj})


# ==============================================================================
# LANDING PAGE CMS VIEWS
# ==============================================================================

@sa_required
def super_admin_landing_overview(request):
    """Overview hub for managing all Landing Page components."""
    context = {
        'branding': SiteBranding.objects.first(),
        'hero': HeroSection.objects.first(),
        'qs_cards_count': QuickServiceCard.objects.count(),
        'featured_count': FeaturedProjectCard.objects.count(),
        'packages_count': PackageCard.objects.count(),
        'testimonials_count': Testimonial.objects.count(),
    }
    return render(request, 'superadmin/cms_landing_overview.html', context)


# ── BRANDING ──────────────────────────────────────────────────────────────────
@sa_required
def super_admin_landing_branding(request):
    branding_obj, _ = SiteBranding.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = SiteBrandingForm(request.POST, request.FILES, instance=branding_obj)
        if form.is_valid():
            form.save()
            django_messages.success(request, 'Site Branding updated successfully!')
            return redirect('super_admin_landing_branding')
    else:
        form = SiteBrandingForm(instance=branding_obj)
    return render(request, 'superadmin/cms_branding.html', {'form': form, 'branding': branding_obj})


# ── HERO SECTION ──────────────────────────────────────────────────────────────
@sa_required
def super_admin_landing_hero(request):
    hero_obj, _ = HeroSection.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = HeroSectionForm(request.POST, request.FILES, instance=hero_obj)
        if form.is_valid():
            form.save()
            django_messages.success(request, 'Hero Section updated successfully!')
            return redirect('super_admin_landing_hero')
    else:
        form = HeroSectionForm(instance=hero_obj)
    return render(request, 'superadmin/cms_hero.html', {'form': form, 'hero': hero_obj})


# ── QUICK SERVICES CARDS ──────────────────────────────────────────────────────
@sa_required
def super_admin_landing_quick_services(request):
    cards_qs = QuickServiceCard.objects.all().order_by('order', '-created_at')
    paginator = Paginator(cards_qs, 10)
    page_num = request.GET.get('page', 1)
    try:
        cards = paginator.page(page_num)
    except (EmptyPage, PageNotAnInteger):
        cards = paginator.page(1)
    page_range = paginator.get_elided_page_range(cards.number, on_each_side=2, on_ends=1)
    return render(request, 'superadmin/cms_quick_services.html', {'cards': cards, 'page_range': page_range})

@sa_required
def super_admin_landing_quick_service_create(request):
    if request.method == 'POST':
        form = QuickServiceCardForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            django_messages.success(request, 'Quick Service Card created successfully!')
            return redirect('super_admin_landing_quick_services')
    else:
        form = QuickServiceCardForm()
    return render(request, 'superadmin/cms_card_form.html', {
        'form': form,
        'title': 'Add Quick Service Card',
        'back_url': 'super_admin_landing_quick_services'
    })

@sa_required
def super_admin_landing_quick_service_edit(request, card_id):
    card = get_object_or_404(QuickServiceCard, pk=card_id)
    if request.method == 'POST':
        form = QuickServiceCardForm(request.POST, request.FILES, instance=card)
        if form.is_valid():
            form.save()
            django_messages.success(request, 'Quick Service Card updated successfully!')
            return redirect('super_admin_landing_quick_services')
    else:
        form = QuickServiceCardForm(instance=card)
    return render(request, 'superadmin/cms_card_form.html', {
        'form': form,
        'card': card,
        'title': f'Edit Card: {card.title}',
        'back_url': 'super_admin_landing_quick_services'
    })

@sa_required
def super_admin_landing_quick_service_delete(request, card_id):
    card = get_object_or_404(QuickServiceCard, pk=card_id)
    card.delete()
    django_messages.success(request, 'Quick Service Card deleted.')
    return redirect('super_admin_landing_quick_services')

@sa_required
def super_admin_landing_quick_service_toggle(request, card_id):
    card = get_object_or_404(QuickServiceCard, pk=card_id)
    card.is_active = not card.is_active
    card.save()
    django_messages.success(request, f'Card "{card.title}" {"activated" if card.is_active else "deactivated"}.')
    return redirect('super_admin_landing_quick_services')


# ── FEATURED PROJECTS (BIDDING SHOWCASE) ──────────────────────────────────────
@sa_required
def super_admin_landing_featured_projects(request):
    cards_qs = FeaturedProjectCard.objects.all().order_by('order', '-created_at')
    paginator = Paginator(cards_qs, 10)
    page_num = request.GET.get('page', 1)
    try:
        cards = paginator.page(page_num)
    except (EmptyPage, PageNotAnInteger):
        cards = paginator.page(1)
    page_range = paginator.get_elided_page_range(cards.number, on_each_side=2, on_ends=1)
    return render(request, 'superadmin/cms_featured_projects.html', {'cards': cards, 'page_range': page_range})

@sa_required
def super_admin_landing_featured_project_create(request):
    if request.method == 'POST':
        form = FeaturedProjectCardForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            django_messages.success(request, 'Featured Project Card created!')
            return redirect('super_admin_landing_featured_projects')
    else:
        form = FeaturedProjectCardForm()
    return render(request, 'superadmin/cms_card_form.html', {
        'form': form,
        'title': 'Add Featured Project Card',
        'back_url': 'super_admin_landing_featured_projects'
    })

@sa_required
def super_admin_landing_featured_project_edit(request, card_id):
    card = get_object_or_404(FeaturedProjectCard, pk=card_id)
    if request.method == 'POST':
        form = FeaturedProjectCardForm(request.POST, request.FILES, instance=card)
        if form.is_valid():
            form.save()
            django_messages.success(request, 'Featured Project Card updated!')
            return redirect('super_admin_landing_featured_projects')
    else:
        form = FeaturedProjectCardForm(instance=card)
    return render(request, 'superadmin/cms_card_form.html', {
        'form': form,
        'card': card,
        'title': f'Edit Project: {card.title}',
        'back_url': 'super_admin_landing_featured_projects'
    })

@sa_required
def super_admin_landing_featured_project_delete(request, card_id):
    card = get_object_or_404(FeaturedProjectCard, pk=card_id)
    card.delete()
    django_messages.success(request, 'Featured Project Card deleted.')
    return redirect('super_admin_landing_featured_projects')

@sa_required
def super_admin_landing_featured_project_toggle(request, card_id):
    card = get_object_or_404(FeaturedProjectCard, pk=card_id)
    card.is_active = not card.is_active
    card.save()
    django_messages.success(request, f'Project "{card.title}" status changed.')
    return redirect('super_admin_landing_featured_projects')


# ── PACKAGES & PRICING ────────────────────────────────────────────────────────
@sa_required
def super_admin_landing_packages(request):
    packages_qs = PackageCard.objects.all().order_by('order', '-created_at')
    paginator = Paginator(packages_qs, 10)
    page_num = request.GET.get('page', 1)
    try:
        packages = paginator.page(page_num)
    except (EmptyPage, PageNotAnInteger):
        packages = paginator.page(1)
    page_range = paginator.get_elided_page_range(packages.number, on_each_side=2, on_ends=1)
    return render(request, 'superadmin/cms_packages.html', {'packages': packages, 'page_range': page_range})

@sa_required
def super_admin_landing_package_create(request):
    if request.method == 'POST':
        form = PackageCardForm(request.POST)
        if form.is_valid():
            form.save()
            django_messages.success(request, 'Service Package created!')
            return redirect('super_admin_landing_packages')
    else:
        form = PackageCardForm()
    return render(request, 'superadmin/cms_card_form.html', {
        'form': form,
        'title': 'Add Service Package',
        'back_url': 'super_admin_landing_packages'
    })

@sa_required
def super_admin_landing_package_edit(request, card_id):
    pkg = get_object_or_404(PackageCard, pk=card_id)
    if request.method == 'POST':
        form = PackageCardForm(request.POST, instance=pkg)
        if form.is_valid():
            form.save()
            django_messages.success(request, 'Service Package updated!')
            return redirect('super_admin_landing_packages')
    else:
        form = PackageCardForm(instance=pkg)
    return render(request, 'superadmin/cms_card_form.html', {
        'form': form,
        'card': pkg,
        'title': f'Edit Package: {pkg.title}',
        'back_url': 'super_admin_landing_packages'
    })

@sa_required
def super_admin_landing_package_delete(request, card_id):
    pkg = get_object_or_404(PackageCard, pk=card_id)
    pkg.delete()
    django_messages.success(request, 'Package deleted.')
    return redirect('super_admin_landing_packages')

@sa_required
def super_admin_landing_package_toggle(request, card_id):
    pkg = get_object_or_404(PackageCard, pk=card_id)
    pkg.is_active = not pkg.is_active
    pkg.save()
    django_messages.success(request, f'Package "{pkg.title}" status updated.')
    return redirect('super_admin_landing_packages')


# ── TESTIMONIALS ──────────────────────────────────────────────────────────────
@sa_required
def super_admin_landing_testimonials(request):
    testimonials_qs = Testimonial.objects.all().order_by('order', '-created_at')
    paginator = Paginator(testimonials_qs, 10)
    page_num = request.GET.get('page', 1)
    try:
        testimonials = paginator.page(page_num)
    except (EmptyPage, PageNotAnInteger):
        testimonials = paginator.page(1)
    page_range = paginator.get_elided_page_range(testimonials.number, on_each_side=2, on_ends=1)
    return render(request, 'superadmin/cms_testimonials.html', {'testimonials': testimonials, 'page_range': page_range})

@sa_required
def super_admin_landing_testimonial_create(request):
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            django_messages.success(request, 'Testimonial created!')
            return redirect('super_admin_landing_testimonials')
    else:
        form = TestimonialForm()
    return render(request, 'superadmin/cms_card_form.html', {
        'form': form,
        'title': 'Add Testimonial',
        'back_url': 'super_admin_landing_testimonials'
    })

@sa_required
def super_admin_landing_testimonial_edit(request, card_id):
    item = get_object_or_404(Testimonial, pk=card_id)
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            django_messages.success(request, 'Testimonial updated!')
            return redirect('super_admin_landing_testimonials')
    else:
        form = TestimonialForm(instance=item)
    return render(request, 'superadmin/cms_card_form.html', {
        'form': form,
        'card': item,
        'title': f'Edit Testimonial: {item.client_name}',
        'back_url': 'super_admin_landing_testimonials'
    })

@sa_required
def super_admin_landing_testimonial_delete(request, card_id):
    item = get_object_or_404(Testimonial, pk=card_id)
    item.delete()
    django_messages.success(request, 'Testimonial deleted.')
    return redirect('super_admin_landing_testimonials')

@sa_required
def super_admin_landing_testimonial_toggle(request, card_id):
    item = get_object_or_404(Testimonial, pk=card_id)
    item.is_active = not item.is_active
    item.save()
    django_messages.success(request, f'Testimonial for "{item.client_name}" status updated.')
    return redirect('super_admin_landing_testimonials')

