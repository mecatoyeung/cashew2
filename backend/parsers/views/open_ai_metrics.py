from datetime import datetime

from rest_framework import (
    viewsets,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from parsers.models.open_ai_metrics import OpenAIMetrics

from parsers.serializers.open_ai_metrics import OpenAIMetricsSerializer

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'parser_id',
                OpenApiTypes.STR,
                description="Filter by parser id."
            ),
            OpenApiParameter(
                'start_date',
                OpenApiTypes.STR,
                description="Filter by start date."
            ),
            OpenApiParameter(
                'end_date',
                OpenApiTypes.STR,
                description="Filter by end date."
            )
        ]
    )
)
class OpenAIMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """ View for manage post processing APIs. """
    serializer_class = OpenAIMetricsSerializer
    queryset = OpenAIMetrics.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Retrieve parsers for authenticated user. """
        queryset = self.queryset

        parser_id = int(self.request.query_params.get("parser_id"))
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        return queryset \
            .filter(
                parser__user=self.request.user,
                parser_id=parser_id,
                date__range=[start_date, end_date]
            ).order_by('id').distinct()

    def get_serializer_class(self):
        """ Return the serializer class for request """
        if self.action == 'create':
            return OpenAIMetricsSerializer
        elif self.action == 'retrieve':
            return OpenAIMetricsSerializer
        elif self.action == 'update':
            return OpenAIMetricsSerializer
        elif self.action == 'list':
            return OpenAIMetricsSerializer
        elif self.action == 'destroy':
            return OpenAIMetricsSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new source. """
        serializer.save()
