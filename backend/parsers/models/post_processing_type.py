from enum import Enum

class PostProcessingType(Enum):

  REDACTION = "REDACTION"

  @classmethod
  def choices(cls):
    return tuple((i.name, i.value) for i in cls)
