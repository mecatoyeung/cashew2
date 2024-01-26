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

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from parsers.models.pre_processing import PreProcessing
from parsers.models.document import Document
from parsers.models.document_page import DocumentPage

from parsers.serializers.document import DocumentSerializer, DocumentUploadSerializer, DocumentDetailSerializer

from parsers.helpers.generate_images_from_pdf import generate_images_from_pdf
from parsers.helpers.parse_pdf_to_xml import parse_pdf_to_xml

from backend.settings import MEDIA_ROOT


class PNGRenderer(renderers.BaseRenderer):
    media_type = 'image/jpg'
    format = 'jpg'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data


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

        if self.action == 'list':
            parser_id = int(self.request.query_params.get("parserId"))

            return queryset.filter(
                parser__user=self.request.user,
                parser_id=parser_id
            ).order_by('-last_modified_at').distinct()

        else:
            parser_id = int(self.request.query_params.get("parserId"))

            return queryset.filter(
                parser__user=self.request.user,
                parser_id=parser_id
            ).order_by('-last_modified_at').distinct()

    def get_serializer_class(self):
        """ Return the serializer class for request """
        if self.action == 'list':
            return DocumentSerializer
        elif self.action == 'create':
            return DocumentUploadSerializer
        elif self.action == "delete":
            return DocumentSerializer

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
            name='Document PDF',
            url_path='searchable-pdf')
    def searchable_pdf(self, request, pk, *args, **kwargs):

        document = Document.objects.get(id=pk)
        preprocessings = PreProcessing.objects.order_by(
            "step").filter(parser_id=document.parser.id)

        folder_path = os.path.join(
            MEDIA_ROOT, 'documents/%s/' % (document.guid))
        abs_pdf_path = os.path.join(folder_path, "ocred.pdf")
        if not os.path.isfile(abs_pdf_path):
            for pre_processing in preprocessings:
                abs_pdf_path = os.path.join(folder_path, "pre_processed-" + pre_processing.id, "output.pdf")
                if os.path.isfile(abs_pdf_path):
                    break

        if not os.path.isfile(abs_pdf_path):
            abs_pdf_path = os.path.join(folder_path, "source_file.pdf")

        pdf_file = open(abs_pdf_path, 'rb')
        return_filename = document.guid + "-searchable.pdf"

        response = Response(File(pdf_file), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % return_filename
        return response

    @action(detail=True,
            methods=['GET'],
            name='Document Image',
            url_path='pages/(?P<page_num>[^/.]+)/image',
            renderer_classes=[PNGRenderer])
    def image(self, request, pk, page_num, *args, **kwargs):

        document = Document.objects.get(id=pk)
        preprocessings = PreProcessing.objects.order_by(
            "-step").filter(parser_id=document.parser.id)

        folder_path = os.path.join(
            MEDIA_ROOT, 'documents/%s/' % (document.guid))
        if len(preprocessings) == 0:
            abs_png_path = os.path.join(folder_path, str(page_num) + ".jpg")
        else:
            last_preprocessing = preprocessings[0]
            abs_png_path = os.path.join(
                folder_path, "pre_processed-" + str(last_preprocessing.id), str(page_num) + ".jpg")
            if not os.path.exists(abs_png_path):
                abs_png_path = os.path.join(
                    folder_path, str(page_num) + ".jpg")

        image_file = open(abs_png_path, 'rb')
        return_filename = document.guid + str(page_num) + ".jpg"

        response = Response(File(image_file), content_type='image/jpg')
        response['Content-Disposition'] = 'attachment; filename="%s"' % return_filename
        return response

    @action(detail=True,
            methods=['POST'],
            name='Mark document as chatbot completed',
            url_path='pages/(?P<page_num>[^/.]+)/mark_as_chatbot_completed')
    def ask_openai_about_pdf_content(self, request, pk, page_num, *args, **kwargs):

        document_page = DocumentPage.objects.get(
            document_id=pk, page_num=page_num)

        document_page.chatbot_completed = request.data["status"]

        document_page.save()

        page_completed = DocumentPage.objects.filter(
            document_id=pk,
            page_num=page_num,
            chatbot_completed=False).count() == 0

        try:

            return Response({"completed": page_completed}, status=200)

        except Exception as e:
            print(e)
