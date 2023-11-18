from io import BytesIO

from rest_framework import serializers
from parsers.serializers.splitting_rule import SplittingRuleSerializer, PostSplittingRuleSerializer

from parsers.models.splitting import Splitting
from parsers.models.splitting_rule import SplittingRule
from parsers.models.splitting_condition import SplittingCondition


class SplittingSerializer(serializers.ModelSerializer):
    """ Serializer for splitting. """
    splitting_rules = SplittingRuleSerializer(
        many=True, required=False, allow_null=False)

    class Meta:
        model = Splitting
        fields = ['id', 'guid', 'parser', 'split_type',
                  "splitting_rules",
                  "no_first_page_rules_matched_operation_type",
                  "no_first_page_rules_matched_route_to_parser",
                  "activated"]
        read_only_fields = ['id']

    def _get_or_create_consecutive_page_splitting_rules(self, consecutive_page_splitting_rules, splitting_rule, splitting):
        """ Handle getting or creating ocr as needed. """
        sort_order = 1
        for consecutive_page_splitting_rule in consecutive_page_splitting_rules:
            consecutive_page_splitting_rule["splitting_id"] = splitting.id
            consecutive_page_splitting_rule["parent_splitting_rule_id"] = splitting_rule.id
            consecutive_page_splitting_rule["sort_order"] = sort_order
            consecutive_page_splitting_conditions = consecutive_page_splitting_rule.pop(
                "splitting_conditions")
            consecutive_page_splitting_rules = consecutive_page_splitting_rule.pop(
                "consecutive_page_splitting_rules", [])

            consecutive_page_splitting_rule_obj, consecutive_page_splitting_rule_created = SplittingRule.objects.get_or_create(
                **consecutive_page_splitting_rule,
            )

            splitting_rule.consecutive_page_splitting_rules.add(
                consecutive_page_splitting_rule_obj)

            self._get_or_create_consecutive_page_splitting_conditions(
                consecutive_page_splitting_conditions, consecutive_page_splitting_rule_obj)

    def _get_or_create_consecutive_page_splitting_conditions(self,
                                                             consecutive_page_splitting_conditions,
                                                             consecutive_page_splitting_rule):
        """ Handle getting or creating ocr as needed. """
        sort_order = 1
        for consecutive_page_splitting_condition in consecutive_page_splitting_conditions:
            consecutive_page_splitting_condition["splitting_rule_id"] = consecutive_page_splitting_rule.id
            consecutive_page_splitting_condition["sort_order"] = sort_order
            consecutive_page_splitting_condition_obj, consecutive_page_splitting_condition_created = SplittingCondition.objects.get_or_create(
                **consecutive_page_splitting_condition,
            )
            sort_order += 1

            consecutive_page_splitting_rule.splitting_conditions.add(
                consecutive_page_splitting_condition_obj)

    def _get_or_create_splitting_rules(self, splitting_rules, splitting):
        """ Handle getting or creating ocr as needed. """
        sort_order = 1
        for splitting_rule in splitting_rules:
            splitting_rule["splitting_id"] = splitting.id
            splitting_rule["sort_order"] = sort_order
            splitting_conditions = splitting_rule.pop(
                "splitting", None)
            splitting_conditions = splitting_rule.pop("splitting_conditions")
            consecutive_page_splitting_rules = splitting_rule.pop(
                "consecutive_page_splitting_rules", [])

            splitting_rule_obj, splitting_rule_created = SplittingRule.objects.get_or_create(
                **splitting_rule,
            )

            splitting.splitting_rules.add(splitting_rule_obj)

            self._get_or_create_consecutive_page_splitting_rules(
                consecutive_page_splitting_rules, splitting_rule_obj, splitting)

            self._get_or_create_splitting_conditions(
                splitting_conditions, splitting_rule_obj)
            sort_order += 1

    def _get_or_create_splitting_conditions(self, splitting_conditions, splitting_rule):
        """ Handle getting or creating ocr as needed. """
        sort_order = 1
        for splitting_condition in splitting_conditions:
            splitting_condition["splitting_rule_id"] = splitting_rule.id
            splitting_condition["sort_order"] = sort_order
            splitting_condition_obj, splitting_condition_created = SplittingCondition.objects.get_or_create(
                **splitting_condition,
            )
            sort_order += 1

            splitting_rule.splitting_conditions.add(splitting_condition_obj)

    def update(self, instance, validated_data):
        """ Create a splitting rule. """
        splitting_id = instance.id
        SplittingCondition.objects.filter(
            splitting_rule__splitting_id=splitting_id
        ).delete()
        SplittingRule.objects.filter(
            splitting_id=splitting_id
        ).delete()
        Splitting.objects.filter(
            id=splitting_id
        ).delete()

        splitting_rules = validated_data.pop("splitting_rules", [])

        splitting_obj, created = Splitting.objects.get_or_create(
            **validated_data,
        )

        self._get_or_create_splitting_rules(splitting_rules, splitting_obj)

        return splitting_obj


class PostSplittingSerializer(SplittingSerializer):
    """ Serializer for splitting. """
    splitting_rules = PostSplittingRuleSerializer(
        many=True, required=False, allow_null=False)
