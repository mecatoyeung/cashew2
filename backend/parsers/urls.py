"""
URL mappings for the recipe app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from .views.parser import ParserViewSet
from .views.rule import RuleViewSet
from .views.routing_rule import RoutingRuleViewSet
from .views.stream import StreamViewSet
from .views.queue import QueueViewSet
from .views.document import DocumentViewSet
from .views.source import SourceViewSet
from .views.integration import IntegrationViewSet


parsers_router = DefaultRouter()
parsers_router.register('', ParserViewSet, basename="parsers")
rules_router = DefaultRouter()
rules_router.register('', RuleViewSet, basename="rules")
routing_rules_router = DefaultRouter()
routing_rules_router.register('', RoutingRuleViewSet, basename="routingRules")
streams_router = DefaultRouter()
streams_router.register('', StreamViewSet, basename="streams")
queues_router = DefaultRouter()
queues_router.register('', QueueViewSet, basename="queues")
documents_router = DefaultRouter()
documents_router.register('', DocumentViewSet, basename="documents")
sources_router = DefaultRouter()
sources_router.register('', SourceViewSet, basename="sources")
integrations_router = DefaultRouter()
integrations_router.register('', IntegrationViewSet, basename="integrations")

app_name = "parsers"

urlpatterns = [
    path('parsers/', include(parsers_router.urls), name="parsers"),
    path('routingRules/', include(routing_rules_router.urls), name="routingRules"),
    path('rules/', include(rules_router.urls), name="rules"),
    path('streams/', include(streams_router.urls), name="streams"),
    path('queues/', include(queues_router.urls), name="queues"),
    path('documents/', include(documents_router.urls), name="documents"),
    path('sources/', include(sources_router.urls), name="sources"),
    path('integrations/', include(integrations_router.urls), name="integrations"),
]