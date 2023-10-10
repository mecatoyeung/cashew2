from enum import Enum

class OCRType(Enum):

  GOOGLE_VISION = "GOOGLE_VISION"

  @classmethod
  def choices(cls):
    return tuple((i.name, i.value) for i in cls)
