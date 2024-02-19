from rest_framework import (
    viewsets,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from parsers.models.open_ai_metrics_key import OpenAIMetricsKey

from parsers.serializers.open_ai_metrics_key import OpenAIMetricsKeySerializer


class OpenAIMetricsKeyViewSet(viewsets.ModelViewSet):
    """ View for manage post processing APIs. """
    serializer_class = OpenAIMetricsKeySerializer
    queryset = OpenAIMetricsKey.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Retrieve parsers for authenticated user. """
        queryset = self.queryset

        return queryset \
            .filter(
                parser__user=self.request.user
            ).order_by('id').distinct()

    def get_serializer_class(self):
        """ Return the serializer class for request """
        if self.action == 'create':
            return OpenAIMetricsKeySerializer
        elif self.action == 'retrieve':
            return OpenAIMetricsKeySerializer
        elif self.action == 'update':
            return OpenAIMetricsKeySerializer
        elif self.action == 'list':
            return OpenAIMetricsKeySerializer
        elif self.action == 'destroy':
            return OpenAIMetricsKeySerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new source. """
        serializer.save()
