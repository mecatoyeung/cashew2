from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from ..models.routing_rule import RoutingRule

from ..serializers.routing_rule import RoutingRuleSerializer


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'parserId',
                OpenApiTypes.INT,
                description="Filter by parser id."
            )
        ]
    )
)
class RoutingRuleViewSet(mixins.DestroyModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):

    serializer_class = RoutingRuleSerializer
    queryset = RoutingRule.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Filter queryset to authenticated user. """
        parser_id = int(self.request.query_params.get('parser_id', 0))

        queryset = self.queryset

        return queryset.filter(
            user=self.request.user,
            parser_id=parser_id
        ).order_by("name").distinct()
