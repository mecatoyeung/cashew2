from enum import Enum

class IntegrationType(Enum):

  XML_INTEGRATION = "XML_INTEGRATION"
  PDF_INTEGRATION = "PDF_INTEGRATION"

  @classmethod
  def choices(cls):
    return tuple((i.name, i.value) for i in cls)
