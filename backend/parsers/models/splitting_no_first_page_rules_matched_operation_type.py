from enum import Enum


class SplittingNoFirstPageRulesMatchedOperationType(Enum):

    REMOVE_THE_PAGE = "REMOVE_THE_PAGE"
    CONTINUE_PARSING = "CONTINUE_PARSING"
    ROUTE_TO_PARSER = "ROUTE_TO_PARSER"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
