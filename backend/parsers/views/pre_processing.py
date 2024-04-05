from rest_framework import (
    viewsets,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core import serializers

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from parsers.models.pre_processing import PreProcessing

from parsers.serializers.pre_processing import PreProcessingSerializer


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'parserId',
                OpenApiTypes.STR,
                description="Filter by parser id."
            )
        ]
    )
)
class PreProcessingViewSet(viewsets.ModelViewSet):
    """ View for manage pre processing APIs. """
    serializer_class = PreProcessingSerializer
    queryset = PreProcessing.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Retrieve parsers for authenticated user. """
        queryset = self.queryset

        if self.action == 'list':
            parser_id = int(self.request.query_params.get("parserId"))

            return queryset.filter(
                parser__owner=self.request.user,
                parser_id=parser_id
            ).order_by('id').distinct()

        else:
            return queryset.filter(
                parser__owner=self.request.user
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
