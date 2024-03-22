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
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Permission

from rest_auth.registration.serializers import RegisterSerializer
from rest_auth.serializers import PasswordChangeSerializer

from core.models.profile import Profile
from core.serializers.profile import ProfileSerializer

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


UserModel = get_user_model()

class MyRegisterSerializer(rest_auth.registration.serializers.RegisterSerializer):
    full_name = serializers.CharField(write_only=True)
    company_name = serializers.CharField(write_only=True)
    country = serializers.CharField(write_only=True)
    is_superuser = serializers.BooleanField(write_only=True)

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'full_name': self.validated_data.get('full_name', ''),
            'company_name': self.validated_data.get('company_name', ''),
            'country': self.validated_data.get('country', ''),
            'is_superuser': self.validated_data.get('is_superuser', ''),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user.is_superuser = self.cleaned_data['is_superuser']

        parser_content_type = ContentType.objects.get(model="parser")
        if Permission.objects.filter(codename='cashew_user_management').count() == 0:
            Permission.objects.create(
                name="Can manage users/groups",
                content_type_id=parser_content_type.id,
                codename="cashew_user_management"
            )

        if Permission.objects.filter(codename='cashew_parser_management').count() == 0:
            Permission.objects.create(
                name="Can manage parsers",
                content_type_id=parser_content_type.id,
                codename="cashew_parser_management"
            )

        if Permission.objects.filter(codename='cashew_parser_assign_permissions').count() == 0:
            Permission.objects.create(
                name="Can assign permissions to parsers",
                content_type_id=parser_content_type.id,
                codename="cashew_parser_assign_permissions"
            )

        user.is_staff = True
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


"""class MyUserSerializer(serializers.ModelSerializer):

    profile = ProfileSerializer(source="profile")

    class Meta:
        model = UserModel
        fields = ['id', 'username', 'email', 'is_superuser', 
                  'first_name', 'last_name',
                  'is_staff', 'is_active',
                  'last_login', 'date_joined',
                  'profile']
        read_only_fields = ['id']"""