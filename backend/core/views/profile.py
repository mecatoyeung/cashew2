from rest_framework import (
    viewsets,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models.profile import Profile

from core.serializers.profile import ProfileRetrieveSerializer, \
    ProfileListSerializer, \
    ProfileCreateSerializer, \
    ProfileUpdateSerializer, \
    ProfileDeleteSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    """ View for manage profile APIs. """
    serializer_class = ProfileRetrieveSerializer
    queryset = Profile.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    lookup_field = 'user__id'

    def get_queryset(self):

        return self.queryset.select_related("user").order_by('id').distinct()

    def get_serializer_class(self):
        if self.action == 'create':
            return ProfileCreateSerializer
        elif self.action == 'retrieve':
            return ProfileRetrieveSerializer
        elif self.action == 'list':
            return ProfileListSerializer
        if self.action == 'update':
            return ProfileUpdateSerializer
        elif self.action == 'delete':
            return ProfileDeleteSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save()

