import os
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import (
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core import serializers

from core.models.profile import Profile

from core.serializers.profile import ProfileRetrieveSerializer, \
    ProfileListSerializer, \
    ProfileCreateSerializer, \
    ProfileUpdateSerializer, \
    ProfileDeleteSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    """ View for manage recipe APIs. """
    serializer_class = ProfileRetrieveSerializer
    queryset = Profile.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    lookup_field = 'user__id'

    def get_queryset(self):

        return self.queryset.select_related("user").filter(
            user=self.request.user
        ).order_by('id').distinct()

    def get_serializer_class(self):
        """ Return the serializer class for request """
        if self.action == 'create':
            return ProfileCreateSerializer
        if self.action == 'update':
            return ProfileUpdateSerializer
        elif self.action == 'retrieve':
            return ProfileRetrieveSerializer
        elif self.action == 'list':
            return ProfileListSerializer
        elif self.action == 'delete':
            return ProfileDeleteSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new rule. """
        serializer.save()
