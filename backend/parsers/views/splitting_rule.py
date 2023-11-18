from rest_framework import (
    viewsets,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core import serializers

from parsers.models.splitting_rule import SplittingRule

from parsers.serializers.splitting_rule import SplittingRuleSerializer, PostSplittingRuleSerializer


class SplittingRuleViewSet(viewsets.ModelViewSet):
    """ View for manage post processing APIs. """
    serializer_class = SplittingRuleSerializer
    queryset = SplittingRule.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Retrieve parsers for authenticated user. """
        queryset = self.queryset

        return queryset.filter(
            splitting__parser__user=self.request.user
        ).order_by('id').distinct()

    def get_serializer_class(self):
        """ Return the serializer class for request """
        if self.action == 'create':
            return SplittingRuleSerializer
        elif self.action == 'retrieve':
            return SplittingRuleSerializer
        elif self.action == 'update':
            return SplittingRuleSerializer
        elif self.action == 'list':
            return SplittingRuleSerializer
        elif self.action == 'destroy':
            return SplittingRuleSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new source. """
        serializer.save()
