from rest_framework import serializers

from django.contrib.auth.models import Group, User, Permission

class GroupSerializer(serializers.ModelSerializer):

    user_ids = serializers.SerializerMethodField()
    permission_codenames = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'user_ids', 'permissions', 'permission_codenames']
        read_only_fields = ['id']

    def get_user_ids(self, instance):
        return map(lambda u: u.id, User.objects.filter(groups__id=instance.id))
    
    def get_permission_codenames(self, instance):
        return map(lambda u: u.codename, Permission.objects.filter(group__id=instance.id))

class GroupCreateSerializer(GroupSerializer):
    
    user_ids = serializers.ListField(child = serializers.IntegerField())
    permission_codenames = serializers.ListField(child = serializers.CharField())
    
    def create(self, validated_data):
        user_ids = validated_data.pop(
            "user_ids", None)
        
        permission_codenames = validated_data.pop(
            "permission_codenames", None)

        """ Create Group. """

        instance = Group.objects.create(**validated_data)

        if user_ids is not None:
            for user_id in user_ids:
                user = User.objects.get(id=user_id)
                instance.user_set.add(user)
        
        instance.user_ids = user_ids

        if permission_codenames is not None:
            permission_objs = Permission.objects.filter(codename__in=permission_codenames)
            instance.permissions.set(permission_objs)

        return instance

class GroupListSerializer(GroupSerializer):
    pass

class GroupRetrieveSerializer(GroupSerializer):
    pass

class GroupUpdateSerializer(GroupSerializer):

    user_ids = serializers.ListField(child = serializers.IntegerField())
    permission_codenames = serializers.ListField(child = serializers.CharField())
    
    def update(self, instance, validated_data):
        user_ids = validated_data.pop(
            "user_ids", None)
        
        permission_codenames = validated_data.pop(
            "permission_codenames", None)

        Group.objects.filter(id=instance.id).delete()

        """ Update User. """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if user_ids is not None:
            for user_id in user_ids:
                user = User.objects.get(id=user_id)
                instance.user_set.add(user)

        instance.user_ids = user_ids

        if permission_codenames is not None:
            permission_objs = Permission.objects.filter(codename__in=permission_codenames)
            instance.permissions.set(permission_objs)

        instance.permission_codenames = permission_codenames

        return instance

class GroupDeleteSerializer(GroupSerializer):
    pass

