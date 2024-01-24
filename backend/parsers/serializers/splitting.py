from io import BytesIO

from rest_framework import serializers
from django.db import transaction

from parsers.models.splitting import Splitting
from parsers.models.splitting_rule import SplittingRule
from parsers.models.splitting_condition import SplittingCondition
from parsers.models.consecutive_page_splitting_rule import ConsecutivePageSplittingRule
from parsers.models.consecutive_page_splitting_condition import ConsecutivePageSplittingCondition
from parsers.models.last_page_splitting_rule import LastPageSplittingRule
from parsers.models.last_page_splitting_condition import LastPageSplittingCondition

from parsers.serializers.splitting_rule import SplittingRuleSerializer, PostSplittingRuleSerializer


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
                "consecutive_page_splitting_conditions")

            consecutive_page_splitting_rule_obj = ConsecutivePageSplittingRule()
            consecutive_page_splitting_rule_obj.sort_order = consecutive_page_splitting_rule[
                "sort_order"]
            consecutive_page_splitting_rule_obj.route_to_parser = None
            consecutive_page_splitting_rule_obj.splitting = splitting
            consecutive_page_splitting_rule_obj.parent_splitting_rule = splitting_rule
            consecutive_page_splitting_rule_obj.save()

            splitting_rule.consecutive_page_splitting_rules.add(
                consecutive_page_splitting_rule_obj)

            self._get_or_create_consecutive_page_splitting_conditions(
                consecutive_page_splitting_conditions, consecutive_page_splitting_rule_obj)
            
            sort_order = sort_order + 1

    def _get_or_create_consecutive_page_splitting_conditions(self,
                                                             consecutive_page_splitting_conditions,
                                                             consecutive_page_splitting_rule):
        """ Handle getting or creating ocr as needed. """
        sort_order = 1
        for consecutive_page_splitting_condition in consecutive_page_splitting_conditions:
            consecutive_page_splitting_condition["consecutive_page_splitting_rule"] = consecutive_page_splitting_rule
            consecutive_page_splitting_condition["sort_order"] = sort_order
            consecutive_page_splitting_condition_obj, consecutive_page_splitting_condition_created = ConsecutivePageSplittingCondition.objects.get_or_create(
                **consecutive_page_splitting_condition,
            )
            sort_order += 1

            consecutive_page_splitting_rule.consecutive_page_splitting_conditions.add(
                consecutive_page_splitting_condition_obj)

    def _get_or_create_last_page_splitting_rules(self, last_page_splitting_rules, splitting_rule, splitting):
        """ Handle getting or creating ocr as needed. """
        sort_order = 1
        for last_page_splitting_rule in last_page_splitting_rules:
            last_page_splitting_rule["splitting_id"] = splitting.id
            last_page_splitting_rule["parent_splitting_rule_id"] = splitting_rule.id
            last_page_splitting_rule["sort_order"] = sort_order
            last_page_splitting_conditions = last_page_splitting_rule.pop(
                "last_page_splitting_conditions")

            last_page_splitting_rule_obj = LastPageSplittingRule()
            last_page_splitting_rule_obj.sort_order = last_page_splitting_rule[
                "sort_order"]
            last_page_splitting_rule_obj.route_to_parser = None
            last_page_splitting_rule_obj.splitting = splitting
            last_page_splitting_rule_obj.parent_splitting_rule = splitting_rule
            last_page_splitting_rule_obj.save()

            splitting_rule.last_page_splitting_rules.add(
                last_page_splitting_rule_obj)

            self._get_or_create_last_page_splitting_conditions(
                last_page_splitting_conditions, last_page_splitting_rule_obj)
            
            sort_order = sort_order + 1

    def _get_or_create_last_page_splitting_conditions(self,
                                                      last_page_splitting_conditions,
                                                      last_page_splitting_rule):
        """ Handle getting or creating ocr as needed. """
        sort_order = 1
        for last_page_splitting_condition in last_page_splitting_conditions:
            last_page_splitting_condition["last_page_splitting_rule"] = last_page_splitting_rule
            last_page_splitting_condition["sort_order"] = sort_order
            last_page_splitting_condition_obj, last_page_splitting_condition_created = LastPageSplittingCondition.objects.get_or_create(
                **last_page_splitting_condition,
            )
            sort_order += 1

            last_page_splitting_rule.last_page_splitting_conditions.add(
                last_page_splitting_condition_obj)

    def _get_or_create_splitting_rules(self, splitting_rules, splitting):
        """ Handle getting or creating ocr as needed. """
        sort_order = 1
        for splitting_rule in splitting_rules:
            splitting_rule["splitting_id"] = splitting.id
            splitting_rule["sort_order"] = sort_order
            splitting_conditions = splitting_rule.pop("splitting_conditions")
            consecutive_page_splitting_rules = splitting_rule.pop(
                "consecutive_page_splitting_rules", [])
            last_page_splitting_rules = splitting_rule.pop(
                "last_page_splitting_rules", [])

            #splitting_rule_obj, splitting_rule_created = SplittingRule.objects.create(
            #    **splitting_rule,
            #)
            splitting_rule_obj = SplittingRule(**splitting_rule)
            splitting_rule_obj.save()

            splitting.splitting_rules.add(splitting_rule_obj)

            self._get_or_create_consecutive_page_splitting_rules(
                consecutive_page_splitting_rules, splitting_rule_obj, splitting)

            self._get_or_create_last_page_splitting_rules(
                last_page_splitting_rules, splitting_rule_obj, splitting)

            self._get_or_create_splitting_conditions(
                splitting_conditions, splitting_rule_obj)
            sort_order += 1

    def _get_or_create_splitting_conditions(self, splitting_conditions, splitting_rule):
        """ Handle getting or creating ocr as needed. """
        sort_order = 1
        for splitting_condition in splitting_conditions:
            splitting_condition["splitting_rule"] = splitting_rule
            splitting_condition["sort_order"] = sort_order
            splitting_condition_obj, splitting_condition_created = SplittingCondition.objects.get_or_create(
                **splitting_condition,
            )
            sort_order += 1

            splitting_rule.splitting_conditions.add(splitting_condition_obj)

    def create(self, instance, validated_data):
        """ Create a splitting rule. """
        splitting_id = instance.id
        SplittingCondition.objects.filter(
            splitting_rule__splitting_id=splitting_id
        ).delete()
        SplittingRule.objects.filter(
            splitting_id=splitting_id
        ).delete()
        ConsecutivePageSplittingRule.objects.filter(
            parent_splitting_rule__splitting_id=splitting_id
        ).delete()
        LastPageSplittingRule.objects.filter(
            parent_splitting_rule__splitting_id=splitting_id
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

    def update(self, instance, validated_data):
        with transaction.atomic():
            """ Create a splitting rule. """
            splitting_id = instance.id
            SplittingCondition.objects.filter(
                splitting_rule__splitting_id=splitting_id
            ).delete()
            SplittingRule.objects.filter(
                splitting_id=splitting_id
            ).delete()
            ConsecutivePageSplittingRule.objects.filter(
                parent_splitting_rule__splitting_id=splitting_id
            ).delete()
            LastPageSplittingRule.objects.filter(
                parent_splitting_rule__splitting_id=splitting_id
            ).delete()

            splitting_rules = validated_data.pop("splitting_rules", [])

            instance.no_first_page_rules_matched_operation_type = validated_data.pop(
                "no_first_page_rules_matched_operation_type")
            instance.no_first_page_rules_matched_route_to_parser = validated_data.pop(
                "no_first_page_rules_matched_route_to_parser")
            instance.activated = validated_data.pop(
                "activated")
            instance.save()

            self._get_or_create_splitting_rules(splitting_rules, instance)

            return instance


class PostSplittingSerializer(SplittingSerializer):
    """ Serializer for splitting. """
    splitting_rules = PostSplittingRuleSerializer(
        many=True, required=False, allow_null=False)
