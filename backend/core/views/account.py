from rest_framework import (
    viewsets,
    mixins
)

from rest_framework.decorators import action

from rest_framework.response import Response

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model

from django.contrib.auth.models import User

from core.serializers.account import AccountSerializer, \
    AccountCreateSerializer, \
    AccountRetrieveSerializer,\
    AccountListSerializer, \
    AccountUpdateSerializer, \
    AccountDeleteSerializer

class AccountViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    
    serializer_class = AccountSerializer
    model = get_user_model()
    queryset = User.objects.select_related("profile")
    authentication_classes = ([TokenAuthentication])
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.select_related("profile")

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.action == 'create':
            return AccountCreateSerializer
        elif self.action == 'retrieve':
            return AccountRetrieveSerializer
        elif self.action == 'list':
            return AccountListSerializer
        elif self.action == 'update':
            return AccountUpdateSerializer
        elif self.action == "delete":
            return AccountDeleteSerializer
        return self.serializer_class
    
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
    
    