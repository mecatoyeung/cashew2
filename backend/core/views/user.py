from rest_framework import (
    viewsets,
    mixins
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from django.contrib.auth import get_user

from django.contrib.auth.models import User
from core.serializers.user import UserSerializer, \
    UserListSerializer, \
    UserCreateSerializer, \
    UserUpdateSerializer, \
    UserDeleteSerializer

class UserViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """ View for manage user APIs. """
    serializer_class = UserSerializer
    model = get_user_model()
    queryset = User.objects.select_related("profile")
    authentication_classes = ([TokenAuthentication])
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.select_related("profile")

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'update':
            return UserUpdateSerializer
        elif self.action == "delete":
            return UserDeleteSerializer
        return self.serializer_class
    
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


    