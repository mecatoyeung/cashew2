from enum import Enum


class ChatBotType(Enum):

    NO_CHATBOT = "NO_CHATBOT"
    OPEN_AI = "OPEN_AI"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
