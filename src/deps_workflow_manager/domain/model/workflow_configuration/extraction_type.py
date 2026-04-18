from enum import Enum

__all__ = ["ExtractionType"]


class ExtractionType(str, Enum):
    PLUGIN = "plugin"
    TEMPLATE = "template"
    PROTOTYPE = "prototype"
    NON = "non"
    AZURE_CLOUD_EXTRACTOR = "azure_cloud_extractor"
