import os

from rest_framework import (
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from parsers.models.rule import Rule
from parsers.models.stream import Stream
from parsers.models.stream_condition import StreamCondition

from parsers.serializers.stream import StreamSerializer, StreamDetailSerializer, StreamPostSerializer

from parsers.helpers.stream_processor import StreamProcessor


class StreamViewSet(viewsets.ModelViewSet):
    """ View for manage recipe APIs. """
    serializer_class = StreamDetailSerializer
    queryset = Stream.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Retrieve parsers for authenticated user. """
        queryset = self.queryset

        return queryset.order_by('id').distinct()

    def get_serializer_class(self):
        """ Return the serializer class for request """
        if self.action == 'list':
            return StreamSerializer
        elif self.action == "create":
            return StreamPostSerializer
        elif self.action == 'update':
            return StreamPostSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new stream. """
        serializer.save()
