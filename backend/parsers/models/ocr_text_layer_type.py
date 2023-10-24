from enum import Enum


class OCRTextLayerType(Enum):

    SOURCE = "SOURCE"
    PREPROCESSING = "PREPROCESSING"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
