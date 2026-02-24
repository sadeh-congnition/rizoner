import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def client(test_client):
    class Wrapper:
        def get(self, path, **kwargs):
            return test_client.get(f"/configuration{path}", **kwargs)

        def post(self, path, **kwargs):
            return test_client.post(f"/configuration{path}", **kwargs)

    return Wrapper()


@pytest.mark.django_db
@patch("django_llm_chat.chat.Chat.create")
def test_test_llm_auth_success(mock_chat_create, client):
    from configuration.models import GlobalLLMConfig

    GlobalLLMConfig.objects.create(
        name=GlobalLLMConfig.NameChoices.REASONING_LLM_MODEL, value="gpt-4"
    )

    mock_chat = MagicMock()
    mock_chat.send_user_msg_to_llm.return_value = "I am an AI."
    mock_chat_create.return_value = mock_chat

    response = client.post("/test-llm-auth")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Success",
        "error": None,
        "answer": "I am an AI.",
    }

    mock_chat_create.assert_called_once()
    mock_chat.send_user_msg_to_llm.assert_called_once_with("gpt-4", "Hi, how are you?")


@pytest.mark.django_db
@patch("django_llm_chat.chat.Chat.create")
def test_test_llm_auth_failure(mock_chat_create, client):
    from configuration.models import GlobalLLMConfig

    GlobalLLMConfig.objects.create(
        name=GlobalLLMConfig.NameChoices.REASONING_LLM_MODEL, value="gpt-4"
    )

    mock_chat = MagicMock()
    mock_chat.send_user_msg_to_llm.side_effect = Exception("API Key not valid")
    mock_chat_create.return_value = mock_chat

    response = client.post("/test-llm-auth")

    # Ninja endpoints without raised HTTPException usually return 200 with the error in the schema.
    assert response.status_code == 200
    assert response.json() == {
        "message": None,
        "error": "API Key not valid",
        "answer": None,
    }
