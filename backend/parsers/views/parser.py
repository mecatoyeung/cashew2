from rest_framework import (
    viewsets,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from ..models.parser import Parser
from ..models.rule import Rule
from ..models.source import Source
from ..models.integration import Integration

from ..serializers.parser import ParserSerializer, ParserUpdateSerializer
from ..serializers.rule import RuleSerializer
from ..serializers.source import SourceSerializer
from ..serializers.integration import IntegrationSerializer

@extend_schema_view(
    get_integrations=extend_schema(
        parameters=[
            OpenApiParameter(
                'type',
                OpenApiTypes.STR,
                description="Filter by integration type."
            )
        ]
    )
)
class ParserViewSet(viewsets.ModelViewSet):
    """ View for manage recipe APIs. """
    serializer_class = ParserSerializer
    queryset = Parser.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
         """ Convert a list of strings to integers. """
         return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """ Retrieve parsers for authenticated user. """
        queryset = self.queryset

        return queryset.filter(
            user=self.request.user
        ).prefetch_related("rules") \
        .order_by('id').distinct()

    def get_serializer_class(self):
        """ Return the serializer class for request """
        if self.action == 'list':
            return ParserSerializer
        elif self.action == 'update':
            return ParserUpdateSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new parser. """
        serializer.save(user=self.request.user)

    @action(detail=False,
            methods=['GET'],
            name='Get Sources for this parser',
            url_path='(?P<pk>[^/.]+)/sources')
    def get_sources(self, request, pk, *args, **kwargs):

        sources = Source.objects.filter(parser_id=pk)

        return Response(SourceSerializer(sources, many=True).data, status=200)

    @action(detail=False,
            methods=['GET'],
            name='Get Rules for this parser',
            url_path='(?P<pk>[^/.]+)/rules')
    def get_rules(self, request, pk, *args, **kwargs):

        rules = Rule.objects.filter(parser_id=pk)

        return Response(RuleSerializer(rules, many=True).data, status=200)
    
    @action(detail=False,
            methods=['GET'],
            name='Get Integrations for this parser',
            url_path='(?P<pk>[^/.]+)/integrations')
    def get_integrations(self, request, pk, *args, **kwargs):

        integrations = Integration.objects.filter(parser_id=pk)

        return Response(IntegrationSerializer(integrations, many=True).data, status=200)
