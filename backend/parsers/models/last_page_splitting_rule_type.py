from enum import Enum

class LastPageSplittingRuleType(Enum):

  BY_CONDITIONS = "BY_CONDITIONS"
  WHEN_OTHER_FIRST_PAGE_SPLITTING_RULES_MATCH = "WHEN_OTHER_FIRST_PAGE_SPLITTING_RULES_MATCH"

  @classmethod
  def choices(cls):
    return tuple((i.name, i.value) for i in cls)
