from rest_framework import (
    viewsets,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core import serializers
from django.db.models import Prefetch

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from parsers.models.splitting import Splitting
from parsers.models.splitting_rule import SplittingRule

from parsers.serializers.splitting import SplittingSerializer, PostSplittingSerializer


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
class SplittingViewSet(viewsets.ModelViewSet):
    """ View for manage post processing APIs. """
    serializer_class = SplittingSerializer
    queryset = Splitting.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Retrieve parsers for authenticated user. """
        queryset = self.queryset

        return queryset \
            .prefetch_related("splitting_rules") \
            .filter(
                parser__user=self.request.user
            ).order_by('id').distinct()

    def get_serializer_class(self):
        """ Return the serializer class for request """
        if self.action == 'create':
            return SplittingSerializer
        elif self.action == 'retrieve':
            return SplittingSerializer
        elif self.action == 'update':
            return SplittingSerializer
        elif self.action == 'list':
            return SplittingSerializer
        elif self.action == 'destroy':
            return SplittingSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new source. """
        serializer.save()
