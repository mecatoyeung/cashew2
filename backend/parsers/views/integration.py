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

from parsers.models.integration import Integration

from parsers.serializers.integration import IntegrationSerializer


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'parser_id',
                OpenApiTypes.STR,
                description="Filter by parser id."
            )
        ]
    )
)
class IntegrationViewSet(viewsets.ModelViewSet):
    """ View for manage recipe APIs. """
    serializer_class = IntegrationSerializer
    queryset = Integration.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Retrieve parsers for authenticated user. """
        queryset = self.queryset

        if self.action == 'list':
            parser_id = int(self.request.query_params.get("parserId"))

            return queryset.filter(
                parser_id=parser_id
            ).order_by('id').distinct()

        else:
            return queryset.order_by('id').distinct()

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
