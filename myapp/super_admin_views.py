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

# ─────────────────────────────────────────────
# USERS  (List + Create + Edit + Delete + Toggle)
# ─────────────────────────────────────────────
@sa_required
def super_admin_users(request):
    users = CustomUser.objects.all().order_by('-date_joined')
    return render(request, 'superadmin/user_manager.html', {'users': users})

@sa_required
def super_admin_user_create(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email', '')
        password = request.POST.get('password')
        role = request.POST.get('role', 'USER')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        if CustomUser.objects.filter(username=username).exists():
            django_messages.error(request, f'Username "{username}" already exists.')
            return redirect('super_admin_user_create')
        
        user = CustomUser.objects.create_user(
            username=username, email=email, password=password,
            role=role, first_name=first_name, last_name=last_name
        )
        if role == 'ADMIN':
            user.is_staff = True
            user.save()
        django_messages.success(request, f'User "{username}" created successfully.')
        return redirect('super_admin_users')
    return render(request, 'superadmin/user_form.html', {'mode': 'create'})

@sa_required
def super_admin_user_edit(request, user_id):
    user_obj = get_object_or_404(CustomUser, pk=user_id)
    if request.method == 'POST':
        user_obj.first_name = request.POST.get('first_name', '')
        user_obj.last_name = request.POST.get('last_name', '')
        user_obj.email = request.POST.get('email', '')
        user_obj.role = request.POST.get('role', user_obj.role)
        user_obj.is_active = request.POST.get('is_active') == 'on'
        new_pass = request.POST.get('password', '')
        if new_pass:
            user_obj.set_password(new_pass)
        if user_obj.role == 'ADMIN':
            user_obj.is_staff = True
        user_obj.save()
        django_messages.success(request, f'User "{user_obj.username}" updated.')
        return redirect('super_admin_users')
    return render(request, 'superadmin/user_form.html', {'mode': 'edit', 'user_obj': user_obj})

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
# VENDORS (List + Edit + Delete)
# ─────────────────────────────────────────────
@sa_required
def super_admin_vendors(request):
    vendors = VendorProfile.objects.all().select_related('user')
    return render(request, 'superadmin/vendors.html', {'vendors': vendors})

@sa_required
def super_admin_vendor_edit(request, vendor_id):
    vendor = get_object_or_404(VendorProfile, pk=vendor_id)
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
    return render(request, 'superadmin/vendor_form.html', {'vendor': vendor})

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
# JOBS (List + Edit Status + Delete)
# ─────────────────────────────────────────────
@sa_required
def super_admin_jobs(request):
    jobs = Job.objects.all().select_related('user', 'category').order_by('-created_at')
    return render(request, 'superadmin/jobs.html', {'jobs': jobs})

@sa_required
def super_admin_job_edit(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    categories = Category.objects.all()
    if request.method == 'POST':
        job.title = request.POST.get('title', job.title)
        job.status = request.POST.get('status', job.status)
        job.budget = request.POST.get('budget', job.budget)
        cat_id = request.POST.get('category')
        if cat_id:
            job.category = get_object_or_404(Category, pk=cat_id)
        job.description = request.POST.get('description', job.description)
        job.save()
        django_messages.success(request, f'Job "{job.title}" updated.')
        return redirect('super_admin_jobs')
    return render(request, 'superadmin/job_form.html', {'job': job, 'categories': categories})

@sa_required
def super_admin_job_delete(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    job.delete()
    django_messages.success(request, 'Job deleted.')
    return redirect('super_admin_jobs')

# ─────────────────────────────────────────────
# QUICK SERVICES (List + Edit + Delete)
# ─────────────────────────────────────────────
@sa_required
def super_admin_quick_services(request):
    qservices = QuickService.objects.all().select_related('user', 'category').order_by('-created_at')
    return render(request, 'superadmin/quick_services.html', {'qservices': qservices})

@sa_required
def super_admin_qs_edit(request, qs_id):
    qs = get_object_or_404(QuickService, pk=qs_id)
    categories = Category.objects.all()
    if request.method == 'POST':
        qs.title = request.POST.get('title', qs.title)
        qs.status = request.POST.get('status', qs.status)
        qs.budget = request.POST.get('budget', qs.budget)
        cat_id = request.POST.get('category')
        if cat_id:
            qs.category = get_object_or_404(Category, pk=cat_id)
        qs.description = request.POST.get('description', qs.description)
        qs.save()
        django_messages.success(request, f'Quick Service "{qs.title}" updated.')
        return redirect('super_admin_quick_services')
    return render(request, 'superadmin/qs_form.html', {'qs': qs, 'categories': categories})

@sa_required
def super_admin_qs_delete(request, qs_id):
    qs = get_object_or_404(QuickService, pk=qs_id)
    qs.delete()
    django_messages.success(request, 'Quick Service deleted.')
    return redirect('super_admin_quick_services')

# ─────────────────────────────────────────────
# BIDS (List + Edit Status + Delete)
# ─────────────────────────────────────────────
@sa_required
def super_admin_bids(request):
    bids = Bid.objects.all().select_related('vendor', 'job', 'quick_service').order_by('-created_at')
    return render(request, 'superadmin/bids.html', {'bids': bids})

@sa_required
def super_admin_bid_edit(request, bid_id):
    bid = get_object_or_404(Bid, pk=bid_id)
    if request.method == 'POST':
        bid.status = request.POST.get('status', bid.status)
        bid.amount = request.POST.get('amount', bid.amount)
        bid.save()
        django_messages.success(request, 'Bid updated.')
        return redirect('super_admin_bids')
    return render(request, 'superadmin/bid_form.html', {'bid': bid})

@sa_required
def super_admin_bid_delete(request, bid_id):
    bid = get_object_or_404(Bid, pk=bid_id)
    bid.delete()
    django_messages.success(request, 'Bid deleted.')
    return redirect('super_admin_bids')

# ─────────────────────────────────────────────
# SUBSCRIPTIONS (List + Delete)
# ─────────────────────────────────────────────
@sa_required
def super_admin_subscriptions(request):
    subscriptions = Subscription.objects.all().select_related('vendor').order_by('-created_at')
    return render(request, 'superadmin/subscriptions.html', {'subscriptions': subscriptions})

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
    msgs = Message.objects.all().select_related('sender', 'receiver').order_by('-created_at')
    return render(request, 'superadmin/messages.html', {'chat_messages': msgs})

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
        'trust_metrics_count': TrustMetric.objects.count(),
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
    cards = QuickServiceCard.objects.all().order_by('order', '-created_at')
    return render(request, 'superadmin/cms_quick_services.html', {'cards': cards})

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
    cards = FeaturedProjectCard.objects.all().order_by('order', '-created_at')
    return render(request, 'superadmin/cms_featured_projects.html', {'cards': cards})

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
    packages = PackageCard.objects.all().order_by('order', '-created_at')
    return render(request, 'superadmin/cms_packages.html', {'packages': packages})

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
    testimonials = Testimonial.objects.all().order_by('order', '-created_at')
    return render(request, 'superadmin/cms_testimonials.html', {'testimonials': testimonials})

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


# ── TRUST METRICS ─────────────────────────────────────────────────────────────
@sa_required
def super_admin_landing_trust_metrics(request):
    metrics = TrustMetric.objects.all().order_by('order')
    return render(request, 'superadmin/cms_trust_metrics.html', {'metrics': metrics})

@sa_required
def super_admin_landing_trust_metric_create(request):
    if request.method == 'POST':
        form = TrustMetricForm(request.POST)
        if form.is_valid():
            form.save()
            django_messages.success(request, 'Trust Metric created!')
            return redirect('super_admin_landing_trust_metrics')
    else:
        form = TrustMetricForm()
    return render(request, 'superadmin/cms_card_form.html', {
        'form': form,
        'title': 'Add Trust Metric',
        'back_url': 'super_admin_landing_trust_metrics'
    })

@sa_required
def super_admin_landing_trust_metric_edit(request, metric_id):
    item = get_object_or_404(TrustMetric, pk=metric_id)
    if request.method == 'POST':
        form = TrustMetricForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            django_messages.success(request, 'Trust Metric updated!')
            return redirect('super_admin_landing_trust_metrics')
    else:
        form = TrustMetricForm(instance=item)
    return render(request, 'superadmin/cms_card_form.html', {
        'form': form,
        'card': item,
        'title': f'Edit Trust Metric: {item.label}',
        'back_url': 'super_admin_landing_trust_metrics'
    })

@sa_required
def super_admin_landing_trust_metric_delete(request, metric_id):
    item = get_object_or_404(TrustMetric, pk=metric_id)
    item.delete()
    django_messages.success(request, 'Trust Metric deleted.')
    return redirect('super_admin_landing_trust_metrics')

@sa_required
def super_admin_landing_trust_metric_toggle(request, metric_id):
    item = get_object_or_404(TrustMetric, pk=metric_id)
    item.is_active = not item.is_active
    item.save()
    django_messages.success(request, f'Trust Metric "{item.label}" status updated.')
    return redirect('super_admin_landing_trust_metrics')

