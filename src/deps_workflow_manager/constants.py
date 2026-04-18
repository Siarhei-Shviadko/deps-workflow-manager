PROJECT_NAME = "workflow-manager"
DESCRIPTION = "Service executes and maintains procesing pipelines."
V1_PREFIX = "/v1"
V2_PREFIX = "/v2"
BASE_API_PREFIX = "/api/workflow-manager"
API_PREFIX = BASE_API_PREFIX + V1_PREFIX
SWAGGER_DOC_URL = "/docs"

DOCUMENT_TYPE_BASE_API_PREFIX = "/api/document-type"
DOCUMENT_BASE_API_PREFIX = "/api/document"
TEMPLATE_BASE_API_PREFIX = "/api/template"
EXTRACTION_BASE_API_PREFIX = "/api/extraction"

DOCUMENTS_EXCHANGER = "Documents"
DOCUMENT_TYPE_EXCHANGER = "DocumentType"
EXTRACTION_EXCHANGER = "Extractor"
QUEUE = "workflow-manager"

COMMANDS_QUEUE = "workflow-manager-commands"
COMMANDS_CHANNEL = "WorkflowManagerCommands"
COMMANDS_REPLIES_CHANNEL = "WorkflowManagerCommandsReplies"
SERVICE_CHANNEL = "WorkflowService"

DOCUMENT_SERVICE_CHANNEL = "DocumentService"
VALIDATION_SERVICE_CHANNEL = "ValidationService"

DOCUMENT_IMPORT_SERVICE_CHANNEL = "DocumentImportCommands"
