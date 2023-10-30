from rest_framework import serializers
from ..serializers.splitting_rule import SplittingRuleSerializer

from ..models.splitting import Splitting
from ..models.splitting_rule import SplittingRule


class SplittingSerializer(serializers.ModelSerializer):
    """ Serializer for splitting. """
    splitting_rules = SplittingRuleSerializer(
        many=True, required=False, allow_null=False)

    class Meta:
        model = Splitting
        fields = ['id', 'guid', 'parser', 'split_type', "splitting_rules"]
        read_only_fields = ['id']


class PostSplittingSerializer(SplittingSerializer):
    pass
