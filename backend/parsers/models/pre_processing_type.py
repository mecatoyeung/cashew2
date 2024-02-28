from enum import Enum


class PreProcessingType(Enum):

    ORIENTATION_DETECTION_OPENCV = "ORIENTATION_DETECTION_OPENCV"
    ORIENTATION_DETECTION_TESSERACT = "ORIENTATION_DETECTION_TESSERACT"
    THRESHOLD_BINARIZATION = "THRESHOLD_BINARIZATION"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
