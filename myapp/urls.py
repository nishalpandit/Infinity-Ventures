from django.urls import re_path, path
from . import views
from . import Api_views
from . import super_admin_views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.user_login_view, name='login'),
    path('register/user/', views.register_user_view, name='register_user'),
    path('register/vendor/', views.register_vendor_view, name='register_vendor'),
    path('logout/', views.user_logout_view, name='logout'),
    path('dashboard.html', views.admin_dashboard, name='dashboard_html_direct'),
    path('dashboard', views.admin_dashboard, name='dashboard_direct'),
    path('admin-dashboard.html', views.admin_dashboard, name='admin_dashboard_html'),
    path('admin-dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/dashboard.html', views.admin_dashboard, name='admin_dashboard_sub_html'),
    path('admin-dashboard/dashboard', views.admin_dashboard, name='admin_dashboard_sub'),
    path('vendor/dashboard', views.vendor_dashboard, name='vendor_dashboard'),
    path('user/dashboard', views.user_dashboard, name='user_dashboard'),
    path('admin-dashboard/create-company-vendor/', views.create_company_vendor_view, name='create_company_vendor'),
    path('api/manage-location/', views.manage_location_view, name='manage_location_view'),

    # Super Admin Dashboard
    path('super-admin/login/', super_admin_views.super_admin_login_view, name='super_admin_login'),
    path('super-admin/', super_admin_views.super_admin_dashboard, name='super_admin_dashboard'),
    
    # Users CRUD
    path('super-admin/users/', super_admin_views.super_admin_users, name='super_admin_users'),
    path('super-admin/users/create/', super_admin_views.super_admin_user_create, name='super_admin_user_create'),
    path('super-admin/users/<int:user_id>/edit/', super_admin_views.super_admin_user_edit, name='super_admin_user_edit'),
    path('super-admin/users/<int:user_id>/delete/', super_admin_views.super_admin_user_delete, name='super_admin_user_delete'),
    path('super-admin/users/<int:user_id>/toggle/', super_admin_views.super_admin_user_toggle, name='super_admin_user_toggle'),
    
    # Vendors CRUD
    path('super-admin/vendors/', super_admin_views.super_admin_vendors, name='super_admin_vendors'),
    path('super-admin/vendors/create/', super_admin_views.super_admin_vendor_create, name='super_admin_vendor_create'),
    path('super-admin/vendors/<int:vendor_id>/edit/', super_admin_views.super_admin_vendor_edit, name='super_admin_vendor_edit'),
    path('super-admin/vendors/<int:vendor_id>/delete/', super_admin_views.super_admin_vendor_delete, name='super_admin_vendor_delete'),
    
    # KYC 
    path('super-admin/kyc/', super_admin_views.super_admin_kyc, name='super_admin_kyc'),
    path('super-admin/kyc/<int:kyc_id>/approve/', super_admin_views.super_admin_kyc_approve, name='super_admin_kyc_approve'),
    path('super-admin/kyc/<int:kyc_id>/reject/', super_admin_views.super_admin_kyc_reject, name='super_admin_kyc_reject'),
    
    # CMS: Categories + Locations
    path('super-admin/cms/', super_admin_views.super_admin_cms, name='super_admin_cms'),
    path('super-admin/cms/category/create/', super_admin_views.super_admin_category_create, name='super_admin_category_create'),
    path('super-admin/cms/category/<int:cat_id>/edit/', super_admin_views.super_admin_category_edit, name='super_admin_category_edit'),
    path('super-admin/cms/category/<int:cat_id>/delete/', super_admin_views.super_admin_category_delete, name='super_admin_category_delete'),
    path('super-admin/cms/location/create/', super_admin_views.super_admin_location_create, name='super_admin_location_create'),
    path('super-admin/cms/location/<int:loc_id>/edit/', super_admin_views.super_admin_location_edit, name='super_admin_location_edit'),
    path('super-admin/cms/location/<int:loc_id>/delete/', super_admin_views.super_admin_location_delete, name='super_admin_location_delete'),
    
    # Jobs CRUD
    path('super-admin/jobs/', super_admin_views.super_admin_jobs, name='super_admin_jobs'),
    path('super-admin/jobs/create/', super_admin_views.super_admin_job_create, name='super_admin_job_create'),
    path('super-admin/jobs/<int:job_id>/edit/', super_admin_views.super_admin_job_edit, name='super_admin_job_edit'),
    path('super-admin/jobs/<int:job_id>/bids/', super_admin_views.super_admin_job_bids, name='super_admin_job_bids'),
    path('super-admin/jobs/<int:job_id>/delete/', super_admin_views.super_admin_job_delete, name='super_admin_job_delete'),
    
    # Quick Services CRUD
    path('super-admin/quick-services/', super_admin_views.super_admin_quick_services, name='super_admin_quick_services'),
    path('super-admin/quick-services/create/', super_admin_views.super_admin_qs_create, name='super_admin_qs_create'),
    path('super-admin/quick-services/<int:qs_id>/edit/', super_admin_views.super_admin_qs_edit, name='super_admin_qs_edit'),
    path('super-admin/quick-services/<int:qs_id>/delete/', super_admin_views.super_admin_qs_delete, name='super_admin_qs_delete'),
    
    # Bids CRUD
    path('super-admin/bids/', super_admin_views.super_admin_bids, name='super_admin_bids'),
    path('super-admin/bids/create/', super_admin_views.super_admin_bid_create, name='super_admin_bid_create'),
    path('super-admin/bids/<int:bid_id>/edit/', super_admin_views.super_admin_bid_edit, name='super_admin_bid_edit'),
    path('super-admin/bids/<int:bid_id>/delete/', super_admin_views.super_admin_bid_delete, name='super_admin_bid_delete'),
    
    # Subscriptions
    path('super-admin/subscriptions/', super_admin_views.super_admin_subscriptions, name='super_admin_subscriptions'),
    path('super-admin/subscriptions/create/', super_admin_views.super_admin_subscription_create, name='super_admin_subscription_create'),
    path('super-admin/subscriptions/<int:sub_id>/delete/', super_admin_views.super_admin_subscription_delete, name='super_admin_subscription_delete'),
    
    # Messages
    path('super-admin/messages/', super_admin_views.super_admin_messages, name='super_admin_messages'),
    path('super-admin/messages/<int:msg_id>/delete/', super_admin_views.super_admin_message_delete, name='super_admin_message_delete'),
    
    # Global Settings
    path('super-admin/settings/', super_admin_views.super_admin_settings, name='super_admin_settings'),

    # Landing Page Dynamic CMS
    path('super-admin/landing/', super_admin_views.super_admin_landing_overview, name='super_admin_landing_overview'),
    path('super-admin/landing/branding/', super_admin_views.super_admin_landing_branding, name='super_admin_landing_branding'),
    path('super-admin/landing/hero/', super_admin_views.super_admin_landing_hero, name='super_admin_landing_hero'),
    
    # Quick Service Cards
    path('super-admin/landing/quick-services/', super_admin_views.super_admin_landing_quick_services, name='super_admin_landing_quick_services'),
    path('super-admin/landing/quick-services/create/', super_admin_views.super_admin_landing_quick_service_create, name='super_admin_landing_quick_service_create'),
    path('super-admin/landing/quick-services/<int:card_id>/edit/', super_admin_views.super_admin_landing_quick_service_edit, name='super_admin_landing_quick_service_edit'),
    path('super-admin/landing/quick-services/<int:card_id>/delete/', super_admin_views.super_admin_landing_quick_service_delete, name='super_admin_landing_quick_service_delete'),
    path('super-admin/landing/quick-services/<int:card_id>/toggle/', super_admin_views.super_admin_landing_quick_service_toggle, name='super_admin_landing_quick_service_toggle'),

    # Featured Projects
    path('super-admin/landing/featured-projects/', super_admin_views.super_admin_landing_featured_projects, name='super_admin_landing_featured_projects'),
    path('super-admin/landing/featured-projects/create/', super_admin_views.super_admin_landing_featured_project_create, name='super_admin_landing_featured_project_create'),
    path('super-admin/landing/featured-projects/<int:card_id>/edit/', super_admin_views.super_admin_landing_featured_project_edit, name='super_admin_landing_featured_project_edit'),
    path('super-admin/landing/featured-projects/<int:card_id>/delete/', super_admin_views.super_admin_landing_featured_project_delete, name='super_admin_landing_featured_project_delete'),
    path('super-admin/landing/featured-projects/<int:card_id>/toggle/', super_admin_views.super_admin_landing_featured_project_toggle, name='super_admin_landing_featured_project_toggle'),

    # Packages
    path('super-admin/landing/packages/', super_admin_views.super_admin_landing_packages, name='super_admin_landing_packages'),
    path('super-admin/landing/packages/create/', super_admin_views.super_admin_landing_package_create, name='super_admin_landing_package_create'),
    path('super-admin/landing/packages/<int:card_id>/edit/', super_admin_views.super_admin_landing_package_edit, name='super_admin_landing_package_edit'),
    path('super-admin/landing/packages/<int:card_id>/delete/', super_admin_views.super_admin_landing_package_delete, name='super_admin_landing_package_delete'),
    path('super-admin/landing/packages/<int:card_id>/toggle/', super_admin_views.super_admin_landing_package_toggle, name='super_admin_landing_package_toggle'),

    # Testimonials
    path('super-admin/landing/testimonials/', super_admin_views.super_admin_landing_testimonials, name='super_admin_landing_testimonials'),
    path('super-admin/landing/testimonials/create/', super_admin_views.super_admin_landing_testimonial_create, name='super_admin_landing_testimonial_create'),
    path('super-admin/landing/testimonials/<int:card_id>/edit/', super_admin_views.super_admin_landing_testimonial_edit, name='super_admin_landing_testimonial_edit'),
    path('super-admin/landing/testimonials/<int:card_id>/delete/', super_admin_views.super_admin_landing_testimonial_delete, name='super_admin_landing_testimonial_delete'),
    path('super-admin/landing/testimonials/<int:card_id>/toggle/', super_admin_views.super_admin_landing_testimonial_toggle, name='super_admin_landing_testimonial_toggle'),

    # General APIs (from Api_views.py)
    path('api/add-user/', Api_views.add_user_api, name='add_user_api'),
    path('api/user-nav-data/', Api_views.user_nav_data_api, name='user_nav_data_api'),
    path('api/add-category/', Api_views.add_category_api, name='add_category_api'),
    path('api/update-category/', Api_views.update_category_api, name='update_category_api'),
    path('api/delete-category/', Api_views.delete_category_api, name='delete_category_api'),

    # Auth APIs for User (Customer) and Vendor (from Api_views.py)
    path('api/user/signup/', Api_views.user_signup_api, name='user_signup_api'),
    path('api/user/signup', Api_views.user_signup_api),
    path('api/user/login/', Api_views.user_login_api, name='user_login_api'),
    path('api/user/login', Api_views.user_login_api),
    path('api/vendor/signup/', Api_views.vendor_signup_api, name='vendor_signup_api'),
    path('api/vendor/signup', Api_views.vendor_signup_api),
    path('api/vendor/login/', Api_views.vendor_login_api, name='vendor_login_api'),
    path('api/vendor/login', Api_views.vendor_login_api),

    # Unified & OTP Auth APIs
    path('api/auth/login/', Api_views.unified_login_api, name='unified_login_api'),
    path('api/auth/login', Api_views.unified_login_api),
    path('api/auth/otp-login/', Api_views.unified_otp_login_api, name='unified_otp_login_api'),
    path('api/auth/otp-login', Api_views.unified_otp_login_api),
    path('api/auth/check-phone/', Api_views.check_phone_api, name='check_phone_api'),
    path('api/auth/check-phone', Api_views.check_phone_api),
    path('api/auth/send-otp/', Api_views.send_otp_api, name='send_otp_api'),
    path('api/auth/send-otp', Api_views.send_otp_api),
    path('api/auth/verify-otp/', Api_views.verify_otp_api, name='verify_otp_api'),
    path('api/auth/verify-otp', Api_views.verify_otp_api),
    path('api/user/otp-signup/', Api_views.user_otp_signup_api, name='user_otp_signup_api'),
    path('api/user/otp-signup', Api_views.user_otp_signup_api),
    path('api/user/otp-login/', Api_views.user_otp_login_api, name='user_otp_login_api'),
    path('api/user/otp-login', Api_views.user_otp_login_api),
    path('api/vendor/otp-signup/', Api_views.vendor_otp_signup_api, name='vendor_otp_signup_api'),
    path('api/vendor/otp-signup', Api_views.vendor_otp_signup_api),
    path('api/vendor/otp-login/', Api_views.vendor_otp_login_api, name='vendor_otp_login_api'),
    path('api/vendor/otp-login', Api_views.vendor_otp_login_api),

    # User Job & Service APIs (Bearer Token Protected)
    path('api/user/post-job/', Api_views.user_post_job_api, name='user_post_job_api'),
    path('api/user/post-job', Api_views.user_post_job_api),
    path('api/user/jobs/create/', Api_views.user_post_job_api, name='user_jobs_create_api'),
    path('api/user/jobs/create', Api_views.user_post_job_api),
    path('api/user/post-quick-service/', Api_views.user_post_quick_service_api, name='user_post_quick_service_api'),
    path('api/user/post-quick-service', Api_views.user_post_quick_service_api),
    path('api/user/quick-services/create/', Api_views.user_post_quick_service_api, name='user_quick_services_create_api'),
    path('api/user/quick-services/create', Api_views.user_post_quick_service_api),

    re_path(r'^(?P<path>.*)$', views.dashboard_view, name='dashboard'),
]
