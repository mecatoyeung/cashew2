from rest_framework import serializers

from core.models.profile import Profile

import core.serializers.account as account


class ProfileSerializer(serializers.ModelSerializer):

    user = account.AccountSerializer(many=False, required=False)

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

