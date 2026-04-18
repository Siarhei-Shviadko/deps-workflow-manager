from enum import Enum

__all__ = ["PluginPipelineStep", "TemplatePipelineStep", "ImportSource", "DEFAULT_OCR_ENGINE"]


class PluginPipelineStep(str, Enum):
    PREPROCESS = "preprocess"
    EXTRACTION = "extraction"


class TemplatePipelineStep(str, Enum):
    PREPROCESS = "preprocess"
    IDENTIFICATION = "identification"
    EXTRACTION = "extraction"


class ImportSource(str, Enum):
    GOOGLE_DRIVE = "GoogleDrive"


DEFAULT_OCR_ENGINE = "TESSERACT"
