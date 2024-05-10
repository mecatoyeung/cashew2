from rest_framework import serializers

from django.contrib.auth.models import Group, User, Permission

from parsers.models.parser import Parser

class GroupSerializer(serializers.ModelSerializer):

    user_set = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(),
        default=None)
    permission_codenames = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'user_set', 'permissions', 'permission_codenames']
        read_only_fields = ['id']

    def get_user_set(self, instance):
        return map(lambda u: u.id, User.objects.filter(groups__id=instance.id))
    
    def get_permission_codenames(self, instance):
        return map(lambda u: u.codename, Permission.objects.filter(group__id=instance.id))

class GroupCreateSerializer(GroupSerializer):
    
    user_set = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(),
        default=None)
    #user_ids = serializers.ListField(child = serializers.IntegerField())
    permission_codenames = serializers.ListField(child = serializers.CharField(), read_only=True)
    
    def create(self, validated_data):
        user_ids = validated_data.pop(
            "user_set", None)
        
        permission_codenames = validated_data.pop(
            "permission_codenames", None)

        """ Create Group. """

        instance = Group.objects.create(**validated_data)

        if user_ids is not None:
            for user_id in user_ids:
                user = User.objects.get(id=user_id)
                instance.user_set.add(user)

        if permission_codenames is not None:
            permission_objs = Permission.objects.filter(codename__in=permission_codenames)
            instance.permissions.set(permission_objs)

        return instance

class GroupListSerializer(GroupSerializer):
    pass

class GroupRetrieveSerializer(GroupSerializer):
    pass

class GroupUpdateSerializer(GroupSerializer):

    user_set = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(),
        default=None)
    #user_ids = serializers.ListField(child = serializers.IntegerField())
    permission_codenames = serializers.ListField(child = serializers.CharField())
    
    def update(self, instance, validated_data):
        user_ids = validated_data.pop(
            "user_set", None)
        
        permission_codenames = validated_data.pop(
            "permission_codenames", None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.user_set.clear()

        if user_ids is not None:
            for user in user_ids:
                instance.user_set.add(user)

        if permission_codenames is not None:
            permission_objs = Permission.objects.filter(codename__in=permission_codenames)
            instance.permissions.set(permission_objs)

        instance.permission_codenames = permission_codenames

        instance.save()

        return instance

class GroupDeleteSerializer(GroupSerializer):
    pass

