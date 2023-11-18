from rest_framework import serializers

from parsers.models.splitting_condition import SplittingCondition


class SplittingConditionSerializer(serializers.ModelSerializer):
    """ Serializer for splitting rules. """
    sort_order = serializers.IntegerField(required=False)
    value = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = SplittingCondition
        fields = ['id', 'rule',
                  'operator', 'value', 'sort_order']
        read_only_fields = ['id']


class PostSplittingConditionSerializer(serializers.ModelSerializer):
    """ Serializer for splitting rules. """
    sort_order = serializers.IntegerField(required=False)
    value = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = SplittingCondition
        fields = ['rule',
                  'operator', 'value', 'sort_order']
