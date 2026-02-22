from ninja import Router, ModelSchema
from .models import Thread

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
    return thread
