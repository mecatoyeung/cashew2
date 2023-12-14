"""
URL mappings for the recipe app.
"""
import sys
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from parsers.models.queue import Queue
from parsers.models.queue_class import QueueClass
from parsers.models.queue_status import QueueStatus
from parsers.models.source import Source

from .views.parser import ParserViewSet
from .views.rule import RuleViewSet
from .views.stream import StreamViewSet
from .views.open_ai import OpenAIViewSet
from .views.queue import QueueViewSet
from .views.document import DocumentViewSet
from .views.source import SourceViewSet
from .views.pre_processing import PreProcessingViewSet
from .views.splitting import SplittingViewSet
from .views.splitting_rule import SplittingRuleViewSet
from .views.chatbot import ChatBotViewSet
from .views.post_processing import PostProcessingViewSet
from .views.integration import IntegrationViewSet


def running_migration(argv):
    for arg in argv:
        if "makemigrations" in arg or "migrate" in arg:
            return True
    return False


parsers_router = DefaultRouter()
parsers_router.register('', ParserViewSet, basename="parsers")
rules_router = DefaultRouter()
rules_router.register('', RuleViewSet, basename="rules")
streams_router = DefaultRouter()
streams_router.register('', StreamViewSet, basename="streams")
openais_router = DefaultRouter()
openais_router.register('', OpenAIViewSet, basename="openais")
queues_router = DefaultRouter()
queues_router.register('', QueueViewSet, basename="queues")
documents_router = DefaultRouter()
documents_router.register('', DocumentViewSet, basename="documents")
sources_router = DefaultRouter()
sources_router.register('', SourceViewSet, basename="sources")
preprocessings_router = DefaultRouter()
preprocessings_router.register(
    '', PreProcessingViewSet, basename="preprocessings")
splittings_router = DefaultRouter()
splittings_router.register('', SplittingViewSet, basename="splittings")
splitting_rules_router = DefaultRouter()
splitting_rules_router.register(
    '', SplittingRuleViewSet, basename="splitting_rules")
chatbots_router = DefaultRouter()
chatbots_router.register('', ChatBotViewSet, basename="chatbots")
postprocessings_router = DefaultRouter()
postprocessings_router.register(
    '', PostProcessingViewSet, basename="postprocessings")
integrations_router = DefaultRouter()
integrations_router.register('', IntegrationViewSet, basename="integrations")

app_name = "parsers"

urlpatterns = [
    path('parsers/', include(parsers_router.urls), name="parsers"),
    path('rules/', include(rules_router.urls), name="rules"),
    path('streams/', include(streams_router.urls), name="streams"),
    path('queues/', include(queues_router.urls), name="queues"),
    path('documents/', include(documents_router.urls), name="documents"),
    path('sources/', include(sources_router.urls), name="sources"),
    path('preprocessings/', include(preprocessings_router.urls),
         name="preprocessings"),
    path('splittings/', include(splittings_router.urls),
         name="splittings"),
    path('splitting_rules/', include(splitting_rules_router.urls),
         name="splitting_rules"),
    path('chatbots/', include(chatbots_router.urls),
         name="chatbots"),
    path('postprocessings/', include(postprocessings_router.urls),
         name="postprocessings"),
    path('integrations/', include(integrations_router.urls), name="integrations"),
]


if not running_migration(sys.argv):
    # Set all Queues from In Progress to Ready
    all_sources = Source.objects.filter(is_running=True)
    for source in all_sources:
        source.is_running = False
        source.save()

    all_in_progress_queues = Queue.objects.filter(
        queue_status=QueueStatus.IN_PROGRESS.value)
    for queue in all_in_progress_queues:
        queue.queue_status = QueueStatus.READY.value
        queue.save()

    all_stopped_queues = Queue.objects.filter(
        queue_status=QueueStatus.STOPPED.value)
    for queue in all_stopped_queues:
        queue.queue_class = QueueClass.PROCESSED.value
        queue.queue_status = QueueStatus.COMPLETED.value
        queue.save()
