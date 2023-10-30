from enum import Enum


class SplittingOperatorType(Enum):

    EQUALS = "EQUALS"
    CONTAINS = "CONTAINS"
    REGEX = "REGEX"
    IS_EMPTY = "IS_EMPTY"
    IS_NOT_EMPTY = "IS_NOT_EMPTY"
    CHANGED = "CHANGED"
    NOT_CHANGED = "NOT_CHANGED"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
