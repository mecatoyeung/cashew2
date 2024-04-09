from rest_framework import serializers

from parsers.models.chatbot import ChatBot


class ChatBotSerializer(serializers.ModelSerializer):

    open_ai_resource_name = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)
    open_ai_api_key = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)
    open_ai_deployment = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)
    open_ai_default_question = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = ChatBot
        fields = ['id', 'guid', 'chatbot_type',
                  'open_ai_resource_name', 'open_ai_api_key', 'open_ai_deployment', 'open_ai_default_question',
                  'base_url']
        read_only_fields = ['id']

    def create(self, validated_data):
        """ Create a chatbot. """
        chatbot = ChatBot.objects.create(**validated_data)

        return chatbot

    def update(self, instance, validated_data):
        """ Update chatbot. """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class ProtectedChatBotSerializer(ChatBotSerializer):

    class Meta:
        model = ChatBot
        fields = ['id', 'guid', 'chatbot_type',
                  'open_ai_default_question',
                  'base_url']
        read_only_fields = ['id']

