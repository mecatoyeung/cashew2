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

from ..models.routing_condition import RoutingCondition

from ..serializers.routing_condition import RoutingConditionSerializer


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'routingRuleId',
                OpenApiTypes.INT,
                description="Filter by routing rule id."
            )
        ]
    )
)
class RoutingConditionViewSet(mixins.DestroyModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):

    serializer_class = RoutingConditionSerializer
    queryset = RoutingCondition.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Filter queryset to authenticated user. """
        routing_rule_id = int(self.request.query_params.get('routingRuleId', 0))

        queryset = self.queryset

        return queryset.filter(
            user=self.request.user,
            routing_rule_id=routing_rule_id
        ).order_by("name").distinct()

