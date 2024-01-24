from enum import Enum


class PreProcessingType(Enum):

    ORIENTATION_DETECTION = "ORIENTATION_DETECTION"
    THRESHOLD_BINARIZATION = "THRESHOLD_BINARIZATION"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
