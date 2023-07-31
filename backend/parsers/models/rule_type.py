from enum import Enum

class RuleType(Enum):

    INPUT_TEXTFIELD = "INPUT_TEXTFIELD"
    INPUT_DROPDOWN = "INPUT_DROPDOWN"
    TEXTFIELD = "TEXTFIELD"
    ANCHORED_TEXTFIELD = "ANCHORED_TEXTFIELD"
    TABLE = "TABLE"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
