from rest_framework import (
    viewsets,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

import requests
import json

from parsers.models.parser import Parser
from parsers.models.document import Document
from parsers.models.chatbot import ChatBot

from parsers.serializers.chatbot import ChatBotSerializer

from parsers.helpers.document_parser import DocumentParser


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
class ChatBotViewSet(viewsets.ModelViewSet):
    """ View for manage post processing APIs. """
    serializer_class = ChatBotSerializer
    queryset = ChatBot.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Retrieve parsers for authenticated user. """
        queryset = self.queryset

        parser_id = int(self.request.query_params.get("parserId"))

        return queryset \
            .filter(
                parser__user=self.request.user,
                parser_id=parser_id
            ).order_by('id').distinct()

    def get_serializer_class(self):
        """ Return the serializer class for request """
        if self.action == 'create':
            return ChatBotSerializer
        elif self.action == 'retrieve':
            return ChatBotSerializer
        elif self.action == 'update':
            return ChatBotSerializer
        elif self.action == 'list':
            return ChatBotSerializer
        elif self.action == 'destroy':
            return ChatBotSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new source. """
        serializer.save()
