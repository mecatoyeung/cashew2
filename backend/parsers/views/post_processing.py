from rest_framework import (
    viewsets,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core import serializers

from ..models.post_processing import PostProcessing

from ..serializers.post_processing import PostProcessingSerializer


class PostProcessingViewSet(viewsets.ModelViewSet):
    """ View for manage post processing APIs. """
    serializer_class = PostProcessingSerializer
    queryset = PostProcessing.objects.all()
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
            return PostProcessingSerializer
        elif self.action == 'retrieve':
            return PostProcessingSerializer
        elif self.action == 'update':
            return PostProcessingSerializer
        elif self.action == 'list':
            return PostProcessingSerializer
        elif self.action == 'destroy':
            return PostProcessingSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new source. """
        serializer.save()
