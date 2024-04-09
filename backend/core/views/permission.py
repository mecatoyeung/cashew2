from rest_framework import (
    viewsets,
    mixins
)

from rest_framework.decorators import action

from rest_framework.response import Response

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model

from django.contrib.auth.models import User,\
    Permission
from core.serializers.permission import PermissionSerializer

class PermissionViewSet(viewsets.GenericViewSet):

    serializer_class = PermissionSerializer

    @action(detail=False,
            methods=['GET'],
            name='Get all user permissions',
            url_path='permissions',
            authentication_classes=[TokenAuthentication],
            permission_classes=[IsAuthenticated],)
    def get_user_permissions(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return Response({ 'permissions': map(lambda x : x.codename, Permission.objects.all()) }, status=200)
        all_permissions = request.user.user_permissions.all() | Permission.objects.filter(group__user=request.user)
        return Response({ 'permissions': map(lambda x : x.codename, all_permissions) }, status=200)
    
    