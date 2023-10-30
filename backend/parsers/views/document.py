import os

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import (
    viewsets,
    renderers
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from django.core.files import File

from backend.settings import MEDIA_URL

from ..models.pre_processing import PreProcessing
from ..models.document import Document
from ..models.document_page import DocumentPage

from ..serializers.document import DocumentSerializer, DocumentUploadSerializer, DocumentDetailSerializer

from ..helpers.generate_images_from_pdf import generate_images_from_pdf
from ..helpers.parse_pdf_to_xml import parse_pdf_to_xml


class PNGRenderer(renderers.BaseRenderer):
    media_type = 'image/png'
    format = 'png'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data


class DocumentViewSet(viewsets.ModelViewSet):
    """ View for manage recipe APIs. """
    serializer_class = DocumentDetailSerializer
    queryset = Document.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """ Convert a list of strings to integers. """
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """ Retrieve parsers for authenticated user. """
        queryset = self.queryset

        return queryset.filter(
            parser__user=self.request.user
        ).order_by('-last_modified_at').distinct()

    def get_serializer_class(self):
        """ Return the serializer class for request """
        if self.action == 'list':
            return DocumentSerializer
        elif self.action == 'create':
            return DocumentUploadSerializer

        return self.serializer_class

    def get_renderer_class(self):
        """ Return the renderer for request """
        if self.action == 'list':
            return JSONRenderer
        elif self.action == 'create':
            return JSONRenderer
        elif self.action == 'image':
            return PNGRenderer

        return JSONRenderer

    def perform_create(self, serializer):
        """ Create a new rule. """
        if serializer.is_valid():
            table_column_separators = serializer.validated_data
            serializer.save()

    @action(detail=True,
            methods=['GET'],
            name='Document Image',
            url_path='pages/(?P<page_num>[^/.]+)',
            renderer_classes=[PNGRenderer])
    def image(self, request, pk, page_num, *args, **kwargs):

        document = Document.objects.get(id=pk)
        preprocessings = PreProcessing.objects.order_by(
            "step").filter(parser_id=document.parser.id)

        folder_path = os.path.join(
            MEDIA_URL, 'documents/%s/' % (document.guid))
        if len(preprocessings) == 0:
            abs_png_path = os.path.join(folder_path, str(page_num) + ".png")
        else:
            last_preprocessing = preprocessings[0]
            abs_png_path = os.path.join(
                folder_path, "pre_processed-" + str(last_preprocessing.id), str(page_num) + ".png")

        image_file = open(abs_png_path, 'rb')
        return_filename = document.guid + str(page_num) + ".png"

        response = Response(File(image_file), content_type='image/png')
        response['Content-Disposition'] = 'attachment; filename="%s"' % return_filename
        return response
