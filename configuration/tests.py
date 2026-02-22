# Create your tests here.
import pytest
from django.test import TestCase
from ninja.testing import TestClient
from configuration.api import router
from configuration.models import GlobalLLMConfig


@pytest.mark.django_db
def test_list_llm_configs_empty():
    client = TestClient(router)
    response = client.get("/llm-config")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.django_db
def test_set_and_list_llm_configs():
    client = TestClient(router)
    
    # Set tool calling model
    payload1 = {
        "name": GlobalLLMConfig.NameChoices.TOOL_CALLING_LLM_MODEL,
        "value": "gpt-4o"
    }
    response1 = client.post("/llm-config", json=payload1)
    assert response1.status_code == 200
    assert response1.json() == payload1
    
    # Check it was listed
    list_response = client.get("/llm-config")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0] == payload1
    
    # Update tool calling model
    payload_update = {
        "name": GlobalLLMConfig.NameChoices.TOOL_CALLING_LLM_MODEL,
        "value": "claude-3-5-sonnet-20241022"
    }
    response2 = client.post("/llm-config", json=payload_update)
    assert response2.status_code == 200
    assert response2.json() == payload_update
    
    # Check it was updated
    list_response2 = client.get("/llm-config")
    assert list_response2.status_code == 200
    assert len(list_response2.json()) == 1
    assert list_response2.json()[0] == payload_update
