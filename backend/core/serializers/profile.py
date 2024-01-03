from rest_framework import serializers
from django.contrib.auth.models import User

from core.models.profile import Profile

from core.serializers.user import UserSerializer


class ProfileSerializer(serializers.ModelSerializer):

    user = UserSerializer(many=False, required=False)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'full_name', 'company_name', 'country']
        read_only_fields = ['id']


class ProfileCreateSerializer(ProfileSerializer):
    pass


class ProfileListSerializer(ProfileSerializer):
    pass


class ProfileRetrieveSerializer(ProfileSerializer):
    pass


class ProfileUpdateSerializer(ProfileSerializer):
    pass


class ProfileDeleteSerializer(ProfileSerializer):
    pass
