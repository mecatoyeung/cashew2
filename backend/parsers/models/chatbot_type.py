from enum import Enum


class ChatBotType(Enum):

    NO_CHATBOT = "NO_CHATBOT"
    OPEN_AI = "OPEN_AI"
    ON_PREMISE_AI = "ON_PREMISE_AI"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
