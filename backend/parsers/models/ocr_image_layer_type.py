from enum import Enum


class OCRImageLayerType(Enum):

    SOURCE = "SOURCE"
    PREPROCESSING = "PREPROCESSING"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
