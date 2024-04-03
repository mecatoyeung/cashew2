import os

from rest_framework import (
    viewsets,
)

from rest_framework.decorators import action

from rest_framework.response import Response

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.contrib.auth.models import User,\
     Permission

from core.serializers.users import UsersSerializer, \
    UsersCreateSerializer, \
    UsersRetrieveSerializer, \
    UsersListSerializer, \
    UsersUpdateSerializer, \
    UsersDeleteSerializer


class UsersViewSet(viewsets.ModelViewSet):
    
    serializer_class = UsersSerializer
    model = User
    queryset = User.objects.select_related("profile")
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        
        return User.objects.select_related("profile")

    def get_serializer_class(self):
        
        if self.action == 'create':
            return UsersCreateSerializer
        elif self.action == 'retrieve':
            return UsersRetrieveSerializer
        elif self.action == 'list':
            return UsersListSerializer
        elif self.action == 'update':
            return UsersUpdateSerializer
        elif self.action == "delete":
            return UsersDeleteSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False,
            methods=['GET'],
            name='Check if super user exist',
            url_path='superuser_exists',
            permission_classes=[AllowAny], authentication_classes=[])
    def check_if_superuser_exists(self, request, *args, **kwargs):

        superuser_exists = User.objects.filter(is_superuser=True).count() > 0

        return Response({ 'superuser_exists': superuser_exists }, status=200)