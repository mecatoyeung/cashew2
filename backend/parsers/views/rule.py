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
from django.core import serializers

from parsers.models.rule import Rule
from parsers.models.document import Document

from parsers.serializers.rule import RuleSerializer, RuleCreateSerializer, RuleUpdateSerializer

from parsers.helpers.document_parser import DocumentParser
from parsers.helpers.stream_processor import StreamProcessor


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
class RuleViewSet(viewsets.ModelViewSet):
    """ View for manage recipe APIs. """
    serializer_class = RuleSerializer
    queryset = Rule.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Retrieve parsers for authenticated user. """
        queryset = self.queryset.prefetch_related('table_column_separators')

        if self.action == 'list':
            parser_id = int(self.request.query_params.get("parserId"))

            return queryset.filter(
                parser__user=self.request.user,
                parser_id=parser_id
            ).order_by('id').distinct()

        else:
            return queryset.filter(
                parser__user=self.request.user
            ).order_by('id').distinct()

    def get_serializer_class(self):
        """ Return the serializer class for request """
        if self.action == 'create':
            return RuleCreateSerializer
        if self.action == 'update':
            return RuleUpdateSerializer
        elif self.action == 'list':
            return RuleSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new rule. """
        serializer.save()

    @action(detail=True,
            methods=['GET'],
            name='Get Processed Streams',
            url_path='document/(?P<document_id>[^/.]+)/processed_streams')
    def processed_streams(self, request, pk, document_id, *args, **kwargs):

        rule = Rule.objects.select_related('parser').prefetch_related(
            "table_column_separators").get(id=pk)

        document = Document.objects.get(id=document_id)

        document_parser = DocumentParser(rule.parser, document)

        rule_raw_result = document_parser.extract(rule)

        stream_processor = StreamProcessor(rule)

        response = stream_processor.process(rule_raw_result)

        return Response(response, status=200)
