from django.urls import re_path, path
from . import views

urlpatterns = [
    path('', views.user_login_view, name='login'),
    path('register/user/', views.register_user_view, name='register_user'),
    path('register/vendor/', views.register_vendor_view, name='register_vendor'),
    path('logout/', views.user_logout_view, name='logout'),
    path('admin-dashboard.html', views.admin_dashboard, name='admin_dashboard_html'),
    path('admin-dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('vendor/dashboard', views.vendor_dashboard, name='vendor_dashboard'),
    path('user/dashboard', views.user_dashboard, name='user_dashboard'),
    path('api/add-user/', views.add_user_api, name='add_user_api'),
    path('api/user-nav-data/', views.user_nav_data_api, name='user_nav_data_api'),
    path('api/add-category/', views.add_category_api, name='add_category_api'),
    path('api/update-category/', views.update_category_api, name='update_category_api'),
    path('api/delete-category/', views.delete_category_api, name='delete_category_api'),
    path('api/manage-location/', views.manage_location_view, name='manage_location_view'),
    re_path(r'^(?P<path>.*)$', views.dashboard_view, name='dashboard'),
]
