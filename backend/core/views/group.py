import os

from rest_framework import (
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.contrib.auth.models import Group

from core.serializers.group import GroupSerializer,\
    GroupCreateSerializer,\
    GroupRetrieveSerializer,\
    GroupListSerializer,\
    GroupUpdateSerializer,\
    GroupDeleteSerializer


class GroupViewSet(viewsets.ModelViewSet):
    
    serializer_class = GroupSerializer
    model = Group
    queryset = Group.objects
    authentication_classes = ([TokenAuthentication])
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        
        return Group.objects

    def get_serializer_class(self):
        
        if self.action == 'create':
            return GroupCreateSerializer
        elif self.action == 'retrieve':
            return GroupRetrieveSerializer
        elif self.action == 'list':
            return GroupListSerializer
        elif self.action == 'update':
            return GroupUpdateSerializer
        elif self.action == "delete":
            return GroupDeleteSerializer
        return self.serializer_class
