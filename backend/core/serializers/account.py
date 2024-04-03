from rest_framework import serializers

from django.contrib.auth.models import User

from core.models.profile import Profile

class ProfileSerializer(serializers.ModelSerializer):

    full_name = serializers.CharField(required=False)

    class Meta:
        model = Profile
        fields = ['id', 'full_name', 'company_name', 'country']
        read_only_fields = ['id']


class AccountSerializer(serializers.ModelSerializer):

    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email',
                  'first_name', 'last_name',
                  'is_superuser', 'is_staff', 'is_active',
                  'last_login', 'date_joined',
                  'profile']
        read_only_fields = ['id', 'username', 'email',
                            'is_superuser', 'is_staff',
                            'last_login', 'date_joined']
        
    
    
    def update(self, instance, validated_data):

        is_active = validated_data.pop(
            "is_active", instance.is_active)
        
        instance.is_active = is_active

        profile_args = validated_data.pop(
            "profile", instance.profile)
        profile = Profile.objects.get(user__id=instance.id)
        
        profile.full_name = profile_args.get('full_name', profile.full_name)
        profile.company_name = profile_args.get('company_name', profile.company_name)
        profile.country = profile_args.get('country', profile.country)
        profile.save()

        instance.save()
        return instance

class AccountCreateSerializer(AccountSerializer):
    pass

class AccountListSerializer(AccountSerializer):
    pass

class AccountRetrieveSerializer(AccountSerializer):
    pass

class AccountUpdateSerializer(AccountSerializer):
    pass

class AccountDeleteSerializer(AccountSerializer):
    pass

