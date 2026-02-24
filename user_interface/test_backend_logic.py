import pytest
from unittest.mock import patch
from statement.models import Thread
from django_llm_chat.models import Chat
from model_bakery import baker

from user_interface.backend_logic import (
    fetch_threads,
    create_thread,
    create_statement,
    fetch_thread,
    fetch_statements,
    verify_llm_auth_connection,
    check_llm_config,
    save_llm_configs,
)


class DummyResponse:
    def __init__(self, ninja_response):
        self.status_code = ninja_response.status_code
        try:
            self.json_data = ninja_response.json()
        except Exception:
            self.json_data = None

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP Error: {self.status_code}")


@pytest.fixture
def mock_requests(test_client):
    def mock_get(url, *args, **kwargs):
        path = url.split("/api", 1)[1] if "/api" in url else url
        response = test_client.get(path)
        return DummyResponse(response)

    def mock_post(url, json=None, *args, **kwargs):
        path = url.split("/api", 1)[1] if "/api" in url else url
        if json is not None:
            response = test_client.post(path, json=json)
        else:
            response = test_client.post(path)
        return DummyResponse(response)

    with (
        patch("user_interface.backend_logic.requests.get", side_effect=mock_get),
        patch("user_interface.backend_logic.requests.post", side_effect=mock_post),
    ):
        yield


@pytest.mark.django_db
def test_fetch_threads(mock_requests):
    chat = baker.make(Chat)
    thread = baker.make(Thread, chat=chat)

    threads = fetch_threads("http://testserver")
    assert len(threads) == 1
    assert threads[0]["id"] == thread.id


@pytest.mark.django_db
def test_create_thread(mock_requests):
    data = create_thread("http://testserver")
    assert "id" in data
    assert Thread.objects.count() == 1


@pytest.mark.django_db
def test_create_statement(mock_requests):
    chat = baker.make(Chat)
    thread = baker.make(Thread, chat=chat)

    data = create_statement("http://testserver", str(thread.id), "Hello", True)
    assert data["content"] == "Hello"
    assert data["is_main"] is True
    assert thread.statements.count() == 1


@pytest.mark.django_db
def test_fetch_thread(mock_requests):
    chat = baker.make(Chat)
    thread = baker.make(Thread, chat=chat)

    data = fetch_thread("http://testserver", str(thread.id))
    assert data is not None
    assert data["id"] == thread.id


@pytest.mark.django_db
def test_fetch_thread_not_found(mock_requests):
    data = fetch_thread("http://testserver", "999999")
    assert data is None


@pytest.mark.django_db
def test_fetch_statements(mock_requests):
    chat = baker.make(Chat)
    thread = baker.make(Thread, chat=chat)
    create_statement("http://testserver", str(thread.id), "Hello", True)

    stmts = fetch_statements("http://testserver", str(thread.id))
    assert len(stmts) == 1
    assert stmts[0]["content"] == "Hello"


@pytest.mark.django_db
def test_check_and_save_llm_config(mock_requests):
    configs = check_llm_config("http://testserver")
    assert len(configs) == 0

    save_llm_configs("http://testserver", [("reasoning_llm_model", "gpt-4")])
    configs = check_llm_config("http://testserver")
    assert len(configs) == 1
    assert configs[0]["name"] == "reasoning_llm_model"
    assert configs[0]["value"] == "gpt-4"


@pytest.mark.django_db
def test_test_llm_auth(mock_requests):
    save_llm_configs("http://testserver", [("reasoning_llm_model", "gpt-4")])

    with patch(
        "django_llm_chat.chat.Chat.send_user_msg_to_llm",
        return_value="Mock LLM response",
    ):
        data = verify_llm_auth_connection("http://testserver")
        assert data["message"] == "Success"
        assert data["answer"] == "Mock LLM response"
