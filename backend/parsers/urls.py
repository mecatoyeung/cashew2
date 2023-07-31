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
from .views.queue import QueueViewSet
from .views.document import DocumentViewSet


parsers_router = DefaultRouter()
parsers_router.register('', ParserViewSet, basename="parsers")
rules_router = DefaultRouter()
rules_router.register('', RuleViewSet, basename="rules")
routing_rules_router = DefaultRouter()
routing_rules_router.register('', RoutingRuleViewSet, basename="routingRules")
queues_router = DefaultRouter()
queues_router.register('', QueueViewSet, basename="queues")
documents_router = DefaultRouter()
documents_router.register('', DocumentViewSet, basename="documents")

app_name = "parsers"

urlpatterns = [
    path('parsers/', include(parsers_router.urls), name="parsers"),
    path('routingRules/', include(routing_rules_router.urls), name="routingRules"),
    path('rules/', include(rules_router.urls), name="rules"),
    path('queues/', include(queues_router.urls), name="queues"),
    path('documents/', include(documents_router.urls), name="documents"),
]