from enum import Enum


class DocumentExtension(Enum):

    PDF = "PDF"
    PNG = "PNG"
    JPG = "JPG"
    GIF = "GIF"
    TIFF = "TIFF"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
