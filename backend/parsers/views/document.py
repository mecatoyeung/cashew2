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
    create=extend_schema(
        parameters=[
            OpenApiParameter(
                'parserId',
                OpenApiTypes.INT,
                description="Filter by parser id."
            )
        ]
    ),
    image=extend_schema(
        parameters=[
            OpenApiParameter(
                'parserId',
                OpenApiTypes.INT,
                description="Filter by parser id."
            ),
            OpenApiParameter(
                'pageNum',
                OpenApiTypes.INT,
                description="Specify page num."
            )
        ]
    ),
)
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
        parser_id = int(self.request.query_params.get('parserId', 0))

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
            document = serializer.save()

            """ Generate images """
            generate_images_from_pdf(document)
            """ Parse pdf to xml """
            parse_pdf_to_xml(document)

    @action(detail=True, methods=['GET'], name='Get Document Image',
            renderer_classes=[PNGRenderer])
    def image(self, request, *args, **kwargs):

        pk = self.kwargs['pk']
        page_num = self.request.query_params.get('pageNum', 1)

        document = Document.objects.get(id=pk)

        folder_path = os.path.join(MEDIA_URL, 'documents/%s/' % (document.guid))
        abs_png_path = os.path.join(folder_path, "original-" + str(page_num) + ".png")
        image_file  = open(abs_png_path, 'rb')
        return_filename = document.guid + str(page_num) + ".png"

        response = Response(File(image_file), content_type='image/png')
        response['Content-Disposition'] = 'attachment; filename="%s"' % return_filename
        return response

