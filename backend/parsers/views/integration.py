from rest_framework import (
    viewsets,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core import serializers

from ..models.integration import Integration

from ..serializers.integration import IntegrationSerializer


class IntegrationViewSet(viewsets.ModelViewSet):
    """ View for manage recipe APIs. """
    serializer_class = IntegrationSerializer
    queryset = Integration.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Retrieve parsers for authenticated user. """
        queryset = self.queryset

        return queryset.filter(
            parser__user=self.request.user
        ).order_by('id').distinct()

    def get_serializer_class(self):
        """ Return the serializer class for request """
        if self.action == 'create':
            return IntegrationSerializer
        elif self.action == 'retrieve':
            return IntegrationSerializer
        elif self.action == 'update':
            return IntegrationSerializer
        elif self.action == 'list':
            return IntegrationSerializer
        elif self.action == 'destroy':
            return IntegrationSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new source. """
        serializer.save()

