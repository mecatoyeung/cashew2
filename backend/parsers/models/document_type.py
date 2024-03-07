from enum import Enum


class DocumentType(Enum):

    TEMPLATE = "TEMPLATE"
    IMPORT = "IMPORT"
    AICHAT = "AICHAT"
    TRASH = "TRASH"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
