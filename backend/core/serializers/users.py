from rest_framework import serializers

from django.contrib.auth.models import User, Permission

from core.models.profile import Profile

from core.serializers.group import GroupSerializer

class ProfileSerializer(serializers.ModelSerializer):

    full_name = serializers.CharField(required=False)

    class Meta:
        model = Profile
        fields = ['id', 'full_name', 'company_name', 'country']
        read_only_fields = ['id']

class UsersSerializer(serializers.ModelSerializer):

    profile = ProfileSerializer(required=False)
    groups = GroupSerializer(many=True, required=False)
    permission_codenames = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email',
                  'first_name', 'last_name',
                  'is_superuser', 'is_staff', 'is_active',
                  'last_login', 'date_joined',
                  'profile', 
                  'groups',
                  'permission_codenames']
        read_only_fields = ['id', 'username', 'email',
                            'is_superuser', 'is_staff',
                            'last_login', 'date_joined']
        
    def get_permission_codenames(self, instance):   
        return map(lambda u: u.codename, Permission.objects.filter(user__id=instance.id))
        

class UsersCreateSerializer(UsersSerializer):
    pass

class UsersListSerializer(UsersSerializer):
    pass

class UsersRetrieveSerializer(UsersSerializer):
    pass

class UsersUpdateSerializer(UsersSerializer):
    
    permission_codenames = serializers.ListField(child = serializers.CharField())
    
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

        permission_codenames = validated_data.pop(
            "permission_codenames", None)

        instance.user_permissions.clear()
        if permission_codenames is not None:
            permission_objs = Permission.objects.filter(codename__in=permission_codenames)
            for permission_obj in permission_objs:
                instance.user_permissions.add(permission_obj)

        instance.permission_codenames = permission_codenames

        return instance

class UsersDeleteSerializer(UsersSerializer):
    pass

