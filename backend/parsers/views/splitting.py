from rest_framework import (
    viewsets,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core import serializers
from django.db.models import Prefetch

from ..models.splitting import Splitting
from ..models.splitting_rule import SplittingRule

from ..serializers.splitting import SplittingSerializer, PostSplittingSerializer


class SplittingViewSet(viewsets.ModelViewSet):
    """ View for manage post processing APIs. """
    serializer_class = SplittingSerializer
    queryset = Splitting.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Retrieve parsers for authenticated user. """
        queryset = self.queryset

        return queryset \
            .prefetch_related("splitting_rules") \
            .filter(
                parser__user=self.request.user
            ).order_by('id').distinct()

    def get_serializer_class(self):
        """ Return the serializer class for request """
        if self.action == 'create':
            return PostSplittingSerializer
        elif self.action == 'retrieve':
            return PostSplittingSerializer
        elif self.action == 'update':
            return PostSplittingSerializer
        elif self.action == 'list':
            return PostSplittingSerializer
        elif self.action == 'destroy':
            return PostSplittingSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new source. """
        serializer.save()
