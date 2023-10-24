from enum import Enum

class PDFIntegrationType(Enum):

  SOURCE = "SOURCE"
  PRE_PROCESSING = "PRE_PROCESSING"
  OCR = "OCR"
  POST_PROCESSING = "POST_PROCESSING"

  @classmethod
  def choices(cls):
    return tuple((i.name, i.value) for i in cls)
