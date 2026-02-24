import pytest
from model_bakery import baker

from statement.models import Thread, Log
from django_llm_chat.models import Chat


@pytest.fixture
def api_client(test_client):
    class Wrapper:
        def get(self, path, **kwargs):
            return test_client.get(f"/statement{path}", **kwargs)

        def post(self, path, **kwargs):
            return test_client.post(f"/statement{path}", **kwargs)

        def delete(self, path, **kwargs):
            return test_client.delete(f"/statement{path}", **kwargs)

        def put(self, path, **kwargs):
            return test_client.put(f"/statement{path}", **kwargs)

    return Wrapper()


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
def test_get_thread(api_client, setup_data):
    thread = Thread.objects.first()
    response = api_client.get(f"/threads/{thread.id}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == thread.id
    assert "chat" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.django_db
def test_get_thread_not_found(api_client):
    response = api_client.get("/threads/999")
    assert response.status_code == 404


@pytest.mark.django_db
def test_list_statements(api_client, setup_data):
    thread = Thread.objects.first()
    from statement.models import Statement

    Statement.objects.create(thread=thread, content="Test Statement 1", is_main=True)
    Statement.objects.create(thread=thread, content="Test Statement 2", is_main=False)

    response = api_client.get(f"/threads/{thread.id}/statements")

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert data[0]["content"] in ["Test Statement 1", "Test Statement 2"]


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

    # Verify log is created
    log_count = Log.objects.count()
    assert log_count == 1

    log = Log.objects.first()
    assert log.thread_id == thread.id
    assert log.details["action"] == "Created"
    assert log.details["entity_type"] == "New Thread"
    assert log.details["entity_id"] == thread.id


@pytest.mark.django_db
def test_create_statement(api_client, setup_data):
    thread = Thread.objects.first()
    payload = {"content": "This is a main statement.", "is_main": True}
    response = api_client.post(f"/threads/{thread.id}/statements", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "This is a main statement."
    assert data["is_main"] is True
    assert data["thread"] == thread.id

    # Verify statement in db
    from statement.models import Statement

    statement = Statement.objects.filter(id=data["id"]).first()
    assert statement is not None
    assert statement.content == "This is a main statement."

    # Verify log is created for main statement
    # Setup data created 3 threads, which in theory doesn't create logs because they are forced via baker,
    # but let's just check the latest log.
    log = Log.objects.order_by("-created_at").first()
    assert log is not None
    assert log.thread_id == thread.id
    assert log.details["action"] == "Created"
    assert log.details["entity_type"] == "Main Statement"
    assert log.details["entity_id"] == statement.id
