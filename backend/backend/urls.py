"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from rest_auth.registration.views import RegisterView, VerifyEmailView
#from rest_auth.views import PasswordResetView, PasswordResetConfirmView


from .settings import STATIC_URL, STATIC_ROOT

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^api/rest-auth/', include('rest_auth.urls')),
    re_path(r'^api/rest-auth/registration/',
            include('rest_auth.registration.urls')),
    path("account/reset-password/<uidb64>/<token>",
       auth_views.PasswordResetConfirmView.as_view(template_name='account/email/password_reset_form.html'),
       name='password_reset_confirm'),
    re_path(r'^api/', include('user_countries.urls')),
    re_path(r'^api/', include('parsers.urls')),
    re_path(r'^api/', include('core.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name="api-schema"),
    path(
        'api/docs',
        SpectacularSwaggerView.as_view(url_name='api-schema'),
        name='api-docs',
    ),
] + static(STATIC_URL, document_root=STATIC_ROOT)
