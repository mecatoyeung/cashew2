"""
Serializers fro the user API View.
"""
from django.contrib.auth import (
    authenticate,
)
from django.utils.translation import gettext as _

from django.conf import settings

from rest_framework.permissions import IsAuthenticated

from rest_framework import serializers

import rest_auth

from django.contrib.auth import get_user_model

from core.models.profile import Profile

from rest_auth.registration.serializers import RegisterSerializer
from rest_auth.serializers import PasswordChangeSerializer

try:
    from allauth.account import app_settings as allauth_settings
    from allauth.utils import (email_address_exists,
                               get_username_max_length)
    from allauth.account.adapter import get_adapter
    from allauth.account.utils import setup_user_email
    from allauth.socialaccount.helpers import complete_social_login
    from allauth.socialaccount.models import SocialAccount
    from allauth.socialaccount.providers.base import AuthProcess
except ImportError:
    raise ImportError("allauth needs to be added to INSTALLED_APPS.")


class MyRegisterSerializer(rest_auth.registration.serializers.RegisterSerializer):
    full_name = serializers.CharField(write_only=True)
    company_name = serializers.CharField(write_only=True)
    country = serializers.CharField(write_only=True)

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'full_name': self.validated_data.get('full_name', ''),
            'company_name': self.validated_data.get('company_name', ''),
            'country': self.validated_data.get('country', ''),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        profile = Profile()
        profile.user = user
        profile.full_name = self.cleaned_data['full_name']
        profile.company_name = self.cleaned_data['company_name']
        profile.country = self.cleaned_data['country']
        profile.save()
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user
    
class MyPasswordChangeSerializer(PasswordChangeSerializer):
    
    def save(self):
        request = self.context.get('request')
        logged_in_user = request.user
        if not logged_in_user.check_password(request.POST["old_password"]):
            raise Exception("Old password is not correct.")
        
        self.set_password_form.save()
        if not self.logout_on_password_change:
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(self.request, self.user)
