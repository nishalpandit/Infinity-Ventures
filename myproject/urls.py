"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
]

# Media files serving (active in all environments)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

# Static files serving (supports all STATICFILES_DIRS and STATIC_ROOT)
urlpatterns += staticfiles_urlpatterns()

if getattr(settings, 'STATIC_ROOT', None) and settings.STATIC_ROOT.exists():
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]

for s_dir in getattr(settings, 'STATICFILES_DIRS', []):
    if s_dir.exists():
        urlpatterns += [
            re_path(r'^static/(?P<path>.*)$', serve, {'document_root': s_dir}),
        ]

urlpatterns += [
    path('', include('myapp.urls')),
]

