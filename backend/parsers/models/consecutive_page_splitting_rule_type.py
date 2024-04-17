from enum import Enum

class ConsecutivePageSplittingRuleType(Enum):

  BY_CONDITIONS = "BY_CONDITIONS"
  WHEN_OTHER_FIRST_PAGE_SPLITTING_RULES_DO_NOT_MATCH = "WHEN_OTHER_FIRST_PAGE_SPLITTING_RULES_DO_NOT_MATCH"

  @classmethod
  def choices(cls):
    return tuple((i.name, i.value) for i in cls)
