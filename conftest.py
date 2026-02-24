import os
import pytest

os.environ["NINJA_SKIP_REGISTRY"] = "1"

from rizoner.urls import api  # noqa: E402
from ninja.testing import TestClient  # noqa: E402


@pytest.fixture(scope="session")
def test_client():
    return TestClient(api)
