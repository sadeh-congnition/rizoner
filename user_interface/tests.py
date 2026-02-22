import pytest
from unittest.mock import patch
from click.testing import CliRunner
from ninja import NinjaAPI
from ninja.testing import TestClient
from statement.api import router as statement_router
from statement.models import Thread
from django_llm_chat.models import Chat
from model_bakery import baker
from user_interface.management.commands.rizui import command as rizui_command


class DummyResponse:
    def __init__(self, ninja_response):
        self.status_code = ninja_response.status_code
        self.json_data = ninja_response.json()

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("HTTP Error")


test_api = NinjaAPI(urls_namespace="test_client_ns")
test_api.add_router("/statement/", statement_router)


@pytest.fixture(scope="session")
def test_client():
    return TestClient(test_api)


@pytest.mark.django_db
def test_rizui_cli_lists_threads(test_client):
    try:
        chat1 = baker.make(Chat)
        chat2 = baker.make(Chat)
        thread1 = baker.make(Thread, chat=chat1)
        thread2 = baker.make(Thread, chat=chat2)
    except Exception as e:
        pytest.fail(f"Failed to create test data: {e}")

    def mock_requests_get(url, *args, **kwargs):
        path = url.split("/api", 1)[1] if "/api" in url else url
        response = test_client.get(path)
        return DummyResponse(response)

    with patch("requests.get", side_effect=mock_requests_get):
        runner = CliRunner()
        result = runner.invoke(
            rizui_command, ["--api-url", "http://127.0.0.1:8000"], input="/threads\n"
        )

        assert result.exit_code == 0, f"Command failed with output: {result.output}"
        assert "Available Threads" in result.output
        assert str(thread1.id) in result.output
        assert str(thread2.id) in result.output


@pytest.mark.django_db
def test_rizui_cli_no_threads(test_client):
    def mock_requests_get(url, *args, **kwargs):
        path = url.split("/api", 1)[1] if "/api" in url else url
        response = test_client.get(path)
        return DummyResponse(response)

    with patch("requests.get", side_effect=mock_requests_get):
        runner = CliRunner()
        result = runner.invoke(rizui_command, ["--api-url", "http://127.0.0.1:8000"], input="/threads\n")

        assert result.exit_code == 0
        assert "No threads found." in result.output
