__all__ = [
    "WorkflowManagerException",
    "NotFoundError",
    "IllegalArgument",
    "DocumentTypeAlreadyExistsException",
    "DocumentTypeHasAssignedDocuments",
    "RestClientError",
    "WorkflowConfigurationNotFound",
]


class WorkflowManagerException(Exception):
    code = "workflow_manager_exception"


class NotFoundError(WorkflowManagerException):
    code = "not_found_error"


class IllegalArgument(WorkflowManagerException):
    code = "illegal_argument"


class DocumentTypeAlreadyExistsException(WorkflowManagerException):
    code = "document_type_already_exists"


class DocumentTypeHasAssignedDocuments(WorkflowManagerException):
    code = "document_type_has_assigned_documents"


class RestClientError(WorkflowManagerException):
    code = "rest_client_error"


class WorkflowConfigurationNotFound(NotFoundError):
    code = "workflow_configuration_not_found"
