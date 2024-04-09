from rest_framework import serializers

from django.contrib.auth.models import User, Permission


class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = ['id']
        read_only_fields = ['id']
        
    
    