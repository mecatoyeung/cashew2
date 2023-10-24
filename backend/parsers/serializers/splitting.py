from rest_framework import serializers
from ..serializers.splitting_rule import SplittingRuleSerializer

from ..models.splitting import Splitting
from ..models.splitting_rule import SplittingRule

class SplittingSerializer(serializers.ModelSerializer):
    """ Serializer for splitting. """
    spliting_rules = SplittingRuleSerializer(many=False, required=True, allow_null=False)

    class Meta:
        model = Splitting
        fields = ['id', 'guid', 'parser', 'split_type', "spliting_rules"]
        read_only_fields = ['id']


