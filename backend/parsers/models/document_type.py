from enum import Enum


class DocumentType(Enum):

    TEMPLATE = "TEMPLATE"
    IMPORT = "IMPORT"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
