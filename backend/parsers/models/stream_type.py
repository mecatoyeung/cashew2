from enum import Enum


class StreamType(Enum):

    TEXTFIELD = "TEXTFIELD"
    TABLE = "TABLE"
    ACROBAT_FORM = "ACROBAT_FORM"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
