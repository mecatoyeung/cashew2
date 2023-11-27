from enum import Enum


class OCRType(Enum):

    NO_OCR = "NO_OCR"
    GOOGLE_VISION = "GOOGLE_VISION"
    DOCTR = "DOCTR"
    PADDLE_OCR = "PADDLE_OCR"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
