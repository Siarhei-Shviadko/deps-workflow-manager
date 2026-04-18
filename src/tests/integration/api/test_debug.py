import pytest

from deps_workflow_manager import constants


class TestDebug:
    def test_debug_endpoint__return_500(self, client):
        with pytest.raises(ValueError):
            client.get(f"{constants.BASE_API_PREFIX}/debug/500")
