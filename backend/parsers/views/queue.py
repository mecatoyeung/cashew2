import os
import shutil
import glob

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

from django.db import transaction
from django.db.models import Prefetch
from django.db.models import Q
from django.db.models import Count

from parsers.models.parser import Parser
from parsers.models.document import Document
from parsers.models.document_type import DocumentType
from parsers.models.document_page import DocumentPage
from parsers.models.queue import Queue


from parsers.serializers.queue import QueueSerializer

from backend import settings


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
        if self.action == 'list':
            parser_id = self.request.query_params.get('parserId', 0)
            queue_class = self.request.query_params.get('queueClass', [])
            queue_classes = queue_class.split(",")

            return queryset.filter(
                parser_id=parser_id,
                queue_class__in=queue_classes
            ).order_by('id').distinct()
        else:
            return queryset.order_by('id').distinct()

    def get_serializer_class(self):
        """ Return the serializer class for request """
        if self.action == 'list':
            return QueueSerializer
        elif self.action == 'delete':
            return QueueSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new rule. """
        serializer.save()

    def perform_destroy(self, instance):

        # delete documents folder first
        document = Document.objects.get(queue__id=instance.id)
        document_folder = os.path.join(
            settings.MEDIA_ROOT, 'documents', document.guid)
        """files = glob.glob(document_folder)
        for f in files:
            os.remove(f)"""
        shutil.rmtree(document_folder, ignore_errors=True)

        # delete document pages first
        DocumentPage.objects.filter(
            document__queue__id=instance.id).delete()
        # delete document first
        Document.objects.filter(queue__id=instance.id).delete()

        return super().perform_destroy(instance)
    
    @action(detail=False,
            methods=['GET'],
            name="Get Queue",
            url_path='status')
    def queue_status(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            parsers = Parser.objects
        else:
            parsers = Parser.objects.filter(Q(permitted_users=self.request.user) | Q(permitted_groups__pk__in=self.request.user.groups.values_list('id', flat=True)) | Q(owner=self.request.user))
        parser_ids = parsers.values_list('id', flat=True)
        queues = Queue.objects.filter(parser__id__in=parser_ids, document__document_type__in=["AICHAT", "IMPORT"])
        queue_status = list(queues.values('parser__id', 'queue_class') \
            .annotate(count=Count('queue_class')) \
            .order_by())
        return Response(queue_status, status=200)
