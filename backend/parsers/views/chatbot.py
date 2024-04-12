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

from django.contrib.auth.models import User

from parsers.models.parser import Parser
from parsers.models.document import Document
from parsers.models.chatbot import ChatBot

from parsers.serializers.chatbot import ChatBotSerializer, ProtectedChatBotSerializer

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
        queryset = self.queryset.select_related("parser")

        parser_id = int(self.request.query_params.get("parserId"))

        return queryset \
            .filter(
                parser_id=parser_id
            ).order_by('id').distinct()

    def get_serializer_class(self):
        """ Return the serializer class for request """
        if self.action == 'create':
            return ChatBotSerializer
        elif self.action == 'retrieve':
            if self.request.user.is_superuser:
                return ChatBotSerializer
            if self.request.user.has_perm("parsers.cashew_parser_management"):
                obj = self.get_object()
                if obj.parser.owner.id == self.request.user.id:
                    return ChatBotSerializer
                for permitted_user in obj.parser.permitted_users.all():
                    if permitted_user.id == self.request.user.id:
                        return ChatBotSerializer
                for permitted_group in obj.parser.permitted_groups.all():
                    users = User.objects.filter(groups__id=permitted_group.id)
                    for user in users:
                        if user.id == self.request.user.id:
                            return ChatBotSerializer
            return ProtectedChatBotSerializer
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
