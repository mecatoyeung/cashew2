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

from parsers.models.queue import Queue

from parsers.serializers.queue import QueueSerializer


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'parserId',
                OpenApiTypes.INT,
                description="Filter by parser id."
            ),
            OpenApiParameter(
                'queueClass',
                OpenApiTypes.STR,
                description="Filter by queue class."
            )
        ]
    )
)
class QueueViewSet(viewsets.ModelViewSet):
    """ View for manage queue APIs. """
    serializer_class = QueueSerializer
    queryset = Queue.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """ Convert a list of strings to integers. """
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """ Retrieve parsers for authenticated user. """
        queryset = self.queryset
        parser_id = self.request.query_params.get('parserId', 0)
        queue_class = self.request.query_params.get('queueClass', None)

        return queryset.filter(
            parser_id=parser_id,
            parser__user=self.request.user,
            queue_class=queue_class
        ).order_by('id').distinct()

    def get_serializer_class(self):
        """ Return the serializer class for request """
        if self.action == 'list':
            return QueueSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new rule. """
        serializer.save()
