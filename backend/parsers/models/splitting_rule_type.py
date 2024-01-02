from enum import Enum


class SplittingRuleType(Enum):

    FIRST_PAGE = "FIRST_PAGE"
    CONSECUTIVE_PAGE = "CONSECUTIVE_PAGE"
    LAST_PAGE = "LAST_PAGE"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
