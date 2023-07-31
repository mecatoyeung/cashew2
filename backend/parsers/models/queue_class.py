from enum import Enum

class QueueClass(Enum):

  PROCESSED = "PROCESSED"
  IMPORT = "IMPORT"
  PREPROCESSING = "PREPROCESSING"
  SPLIT = "SPLIT"
  PARSING = "PARSING"
  POST_PROCESSING = "POST_PROCESSING"
  INTEGRATION = "INTEGRATION"

  @classmethod
  def choices(cls):
    return tuple((i.name, i.value) for i in cls)