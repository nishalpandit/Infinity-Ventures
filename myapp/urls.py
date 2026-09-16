from django.urls import re_path, path
from . import views
from . import Api_views

urlpatterns = [
    path('', views.user_login_view, name='login'),
    path('register/user/', views.register_user_view, name='register_user'),
    path('register/vendor/', views.register_vendor_view, name='register_vendor'),
    path('logout/', views.user_logout_view, name='logout'),
    path('admin-dashboard.html', views.admin_dashboard, name='admin_dashboard_html'),
    path('admin-dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('vendor/dashboard', views.vendor_dashboard, name='vendor_dashboard'),
    path('user/dashboard', views.user_dashboard, name='user_dashboard'),
    path('admin-dashboard/create-company-vendor/', views.create_company_vendor_view, name='create_company_vendor'),
    path('api/manage-location/', views.manage_location_view, name='manage_location_view'),

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
