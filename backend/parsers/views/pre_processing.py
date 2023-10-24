from rest_framework import (
    viewsets,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core import serializers

from ..models.pre_processing import PreProcessing

from ..serializers.pre_processing import PreProcessingSerializer


class PreProcessingViewSet(viewsets.ModelViewSet):
    """ View for manage pre processing APIs. """
    serializer_class = PreProcessingSerializer
    queryset = PreProcessing.objects.all()
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
            return PreProcessingSerializer
        elif self.action == 'retrieve':
            return PreProcessingSerializer
        elif self.action == 'update':
            return PreProcessingSerializer
        elif self.action == 'list':
            return PreProcessingSerializer
        elif self.action == 'destroy':
            return PreProcessingSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new source. """
        serializer.save()
