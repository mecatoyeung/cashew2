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

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1
from pdfminer.psparser import PSLiteral, PSKeyword
from pdfminer.utils import decode_text

from parsers.models.rule import Rule
from parsers.models.document import Document

from parsers.serializers.rule import RuleSerializer, RuleCreateSerializer, RuleUpdateSerializer

from parsers.helpers.document_parser import DocumentParser
from parsers.helpers.stream_processor import StreamProcessor
from parsers.helpers.path_helpers import source_file_pdf_path


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
                parser_id=parser_id
            ).order_by('id').distinct()

        else:
            return queryset.order_by('id').distinct()

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
            name='Get Acrobat Form Fields Streams',
            url_path='documents/(?P<document_id>[^/.]+)/acrobat_form_fields')
    def acrobat_form_fields(self, request, pk, document_id, *args, **kwargs):

        rule = Rule.objects.select_related('parser').prefetch_related(
            "table_column_separators").get(id=pk)

        document = Document.objects.get(id=document_id)
        
        pdf_path = source_file_pdf_path(document)

        acrobat_form_fields = []

        with open(pdf_path, 'rb') as fp:
            parser = PDFParser(fp)

            doc = PDFDocument(parser)
            res = resolve1(doc.catalog)

            if 'AcroForm' in res:
                #raise ValueError("No AcroForm Found")

                fields = resolve1(doc.catalog['AcroForm'])[
                    'Fields']  # may need further resolving

                for f in fields:
                    field = resolve1(f)
                    name, values = field.get('T'), field.get('V')

                    # decode name
                    name = decode_text(name)

                    acrobat_form_fields.append(name)

        if not rule.acrobat_form_field == "" and not rule.acrobat_form_field in acrobat_form_fields:
            acrobat_form_fields.append(rule.acrobat_form_field)

        return Response(acrobat_form_fields, status=200)

    @action(detail=True,
            methods=['GET'],
            name='Get Processed Streams',
            url_path='documents/(?P<document_id>[^/.]+)/processed_streams')
    def processed_streams(self, request, pk, document_id, *args, **kwargs):

        rule = Rule.objects.select_related('parser').prefetch_related(
            "table_column_separators").get(id=pk)

        document = Document.objects.get(id=document_id)

        document_parser = DocumentParser(rule.parser, document)

        result = document_parser.extract_and_stream(rule, with_processed_stream=True)

        response = result["processed_streams"]

        return Response(response, status=200)
