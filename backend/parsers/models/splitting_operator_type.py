from enum import Enum


class SplittingOperatorType(Enum):

    EQUALS = "EQUALS"
    CONTAINS = "CONTAINS"
    DOES_NOT_CONTAINS = "DOES_NOT_CONTAINS"
    REGEX = "REGEX"
    NOT_REGEX = "NOT_REGEX"
    IS_EMPTY = "IS_EMPTY"
    IS_NOT_EMPTY = "IS_NOT_EMPTY"
    CHANGED = "CHANGED"
    NOT_CHANGED = "NOT_CHANGED"
    ALWAYS_TRUE = "ALWAYS_TRUE"
    ALWAYS_FALSE = "ALWAYS_FALSE"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
