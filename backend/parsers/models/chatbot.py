import uuid

from django.db import models

from parsers.models.chatbot_type import ChatBotType


class ChatBot(models.Model):
    id = models.AutoField(primary_key=True)
    parser = models.OneToOneField(
        "Parser", on_delete=models.CASCADE, related_name="chatbot")
    guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)
    chatbot_type = models.CharField(max_length=255, choices=ChatBotType.choices(
    ), null=True, default=ChatBotType.NO_CHATBOT.value)
    open_ai_resource_name = models.CharField(
        max_length=1024, null=True, blank=True)
    open_ai_api_key = models.CharField(max_length=1024, null=True)
    open_ai_default_question = models.CharField(max_length=1024, null=True)
    base_url = models.CharField(max_length=1024, null=True)

    class Meta:
        db_table = 'chatbots'
