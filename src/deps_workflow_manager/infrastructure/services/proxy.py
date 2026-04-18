from typing import Any, Type

from requests import Response

from deps_workflow_manager.domain.exceptions import (
    RestClientError,
    WorkflowManagerException,
)
from deps_workflow_manager.extras.rest_client import (
    BaseRESTClient,
    DEPSApiKeyAuth,
    DEPSTokenAuth,
)
from deps_workflow_manager.infrastructure.context_vars import user


class GenericRestClient(BaseRESTClient):
    _HTTP_STATUS_EXCEPTION_TYPE_MAPPING: dict[int, Type[WorkflowManagerException]] = {}

    def post(self, url: str, json: dict[str, Any]) -> Any:
        url = f"{self._base_url}{url}"
        response = self._session.post(url=url, json=json)
        self._check_response(response)

        return response.json()

    def get(self, url: str) -> Any:
        url = f"{self._base_url}{url}"
        response = self._session.get(url=url)
        self._check_response(response)

        return response.json()

    def patch(self, url: str, json: dict[str, Any]) -> Any:
        url = f"{self._base_url}{url}"
        response = self._session.patch(url=url, json=json)
        self._check_response(response)

        return response.json()

    def delete(self, url: str) -> None:
        url = f"{self._base_url}{url}"
        response = self._session.delete(url=url)
        self._check_response(response)

    def _set_authentication(self) -> None:
        if self._api_key is not None:
            self._session.auth = DEPSApiKeyAuth(self._api_key)
        else:
            self._session.auth = DEPSTokenAuth(user)

    @classmethod
    def _check_response(cls, response: Response) -> None:
        if (exception_type := cls._HTTP_STATUS_EXCEPTION_TYPE_MAPPING.get(response.status_code)) is not None:
            raise exception_type(response.content)

        if not response.ok:
            raise RestClientError(response.content)
