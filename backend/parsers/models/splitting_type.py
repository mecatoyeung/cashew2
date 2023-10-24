from enum import Enum

class SplittingType(Enum):

  NO_SPLIT = "NO_SPLIT"
  SPLIT_BY_PAGE_NUM = "SPLIT_BY_PAGE_NUM"
  SPLIT_BY_CONDITIONS = "SPLIT_BY_CONDITIONS"

  @classmethod
  def choices(cls):
    return tuple((i.name, i.value) for i in cls)
