import pytest
from ninja.testing import TestClient
from model_bakery import baker

from statement.api import router
from statement.models import Thread
from django_llm_chat.models import Chat


@pytest.fixture
def api_client():
    return TestClient(router)


@pytest.fixture
def setup_data(db):
    chat = baker.make(Chat)
    baker.make(Thread, chat=chat, _quantity=3)


@pytest.mark.django_db
def test_list_threads(api_client, setup_data):
    response = api_client.get("/threads")

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 3
    assert "id" in data[0]
    assert "chat" in data[0]
    assert "created_at" in data[0]
    assert "updated_at" in data[0]


@pytest.mark.django_db
def test_create_thread(api_client):
    response = api_client.post("/threads")

    assert response.status_code == 200

    data = response.json()
    assert "id" in data
    assert "chat" in data

    # Verify it exists in db
    thread_count = Thread.objects.count()
    assert thread_count == 1

    thread = Thread.objects.first()
    assert thread.id == data["id"]
    assert thread.chat_id == data["chat"]
