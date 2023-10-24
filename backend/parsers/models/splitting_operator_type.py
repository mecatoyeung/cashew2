from enum import Enum

class SplittingOperatorType(Enum):

  EQUALS = "EQUALS"
  CONTAINS = "CONTAINS"
  REGEX = "REGEX"
  IS_EMPTY = "IS_EMPTY"
  IS_NOT_EMPTY = "IS_NOT_EMPTY"

  @classmethod
  def choices(cls):
    return tuple((i.name, i.value) for i in cls)

