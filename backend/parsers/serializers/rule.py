from rest_framework import serializers

from ..models.rule import Rule

class RuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rule
        fields = ['id',
                  'parser',
                  'name',
                  'rule_type',
                  'pages',
                  'x1',
                  'y1',
                  'x2',
                  'y2',
                  'anchor_text',
                  'anchor_x1',
                  'anchor_y1',
                  'anchor_x2',
                  'anchor_y2',
                  'last_modified_at']
        read_only_fields = ['id']

    def create(self, validated_data):
        """ Create a rule. """
        rule = Rule.objects.create(**validated_data)

        return rule

    def update(self, instance, validated_data):
        """ Update rule. """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class RuleDetailSerializer(RuleSerializer):
    """ Serializer for rule detail view. """

    class Meta(RuleSerializer.Meta):
        fields = RuleSerializer.Meta.fields

