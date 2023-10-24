from enum import Enum


class QueueClass(Enum):

    PROCESSED = "PROCESSED"
    IMPORT = "IMPORT"
    PRE_PROCESSING = "PRE_PROCESSING"
    OCR = "OCR"
    SPLITTING = "SPLITTING"
    PARSING = "PARSING"
    POST_PROCESSING = "POST_PROCESSING"
    INTEGRATION = "INTEGRATION"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
