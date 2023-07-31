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

from ..helpers.stream_processor import StreamProcessor

from ..models.rule import Rule
from ..models.document import Document

from ..serializers.rule import RuleSerializer, RuleDetailSerializer


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'parserId',
                OpenApiTypes.INT,
                description="Filter by parser id."
            )
        ]
    ),
    processed_streams=extend_schema(
        parameters=[
            OpenApiParameter(
                'documentId',
                OpenApiTypes.INT,
                description="Filter by document id."
            )
        ]
    )
)
class RuleViewSet(viewsets.ModelViewSet):
    """ View for manage recipe APIs. """
    serializer_class = RuleDetailSerializer
    queryset = Rule.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
         """ Convert a list of strings to integers. """
         return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """ Retrieve parsers for authenticated user. """
        queryset = self.queryset
        parser_id = self.request.query_params.get('parserId', 0)

        if parser_id == 0:
            return queryset.order_by('id').distinct()
        else:
            return queryset.filter(
                parser_id=parser_id
            ).filter(
                parser__user=self.request.user
            ).order_by('id').distinct()

    def get_serializer_class(self):
        """ Return the serializer class for request """
        if self.action == 'list':
            return RuleSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new rule. """
        serializer.save()

    @action(detail=True, methods=['GET'], name='Get Processed Streams')
    def processed_streams(self, request, *args, **kwargs):

        pk = self.kwargs['pk']
        document_id = self.request.query_params.get('documentId', 0)

        rule = Rule.objects.get(id=pk)
        document = Document.objects.get(id=document_id)

        stream_processor = StreamProcessor(rule)

        response = stream_processor.process(document)

        return Response(response, status=200)