from django.shortcuts import get_object_or_404
from ninja import Router, ModelSchema, Schema
from .models import Thread, Log, Statement

router = Router()


class ThreadSchema(ModelSchema):
    class Meta:
        model = Thread
        fields = ["id", "chat", "created_at", "updated_at"]


@router.get("/threads", response=list[ThreadSchema])
def list_threads(request):
    return Thread.objects.all()


@router.post("/threads", response=ThreadSchema)
def create_thread(request):
    from django_llm_chat.chat import Chat as ChatService

    # Create a new chat session via the ChatService
    chat_service = ChatService.create()

    # Create a new thread linked to this chat session
    thread = Thread.objects.create(chat=chat_service.chat_db_model)

    Log.objects.create(
        thread=thread,
        details={
            "action": "Created",
            "entity_type": "New Thread",
            "entity_id": thread.id,
        },
    )
    return thread


class StatementInSchema(Schema):
    content: str
    is_main: bool = False


class StatementOutSchema(ModelSchema):
    class Meta:
        model = Statement
        fields = ["id", "thread", "content", "is_main", "created_at", "updated_at"]


@router.post("/threads/{thread_id}/statements", response=StatementOutSchema)
def create_statement(request, thread_id: int, payload: StatementInSchema):
    thread = get_object_or_404(Thread, id=thread_id)

    statement = Statement.objects.create(
        thread=thread,
        content=payload.content,
        is_main=payload.is_main,
    )

    if statement.is_main:
        Log.objects.create(
            thread=thread,
            details={
                "action": "Created",
                "entity_type": "Main Statement",
                "entity_id": statement.id,
            },
        )

    return statement
