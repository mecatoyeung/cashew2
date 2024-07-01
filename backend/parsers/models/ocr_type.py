from enum import Enum


class OCRType(Enum):

    NO_OCR = "NO_OCR"
    GOOGLE_VISION = "GOOGLE_VISION"
    DOCTR = "DOCTR"
    PADDLE = "PADDLE"
    OMNIPAGE = "OMNIPAGE"
    APPLE_VISION = "APPLE_VISION"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
