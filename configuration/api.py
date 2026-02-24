from ninja import Router, ModelSchema, Schema
from typing import List
from .models import GlobalLLMConfig

router = Router()


class GlobalLLMConfigSchema(ModelSchema):
    class Meta:
        model = GlobalLLMConfig
        fields = ["name", "value"]


class GlobalLLMConfigInSchema(Schema):
    name: str
    value: str


@router.get("/llm-config", response=List[GlobalLLMConfigSchema])
def list_llm_configs(request):
    return GlobalLLMConfig.objects.all()


@router.post("/llm-config", response=GlobalLLMConfigSchema)
def set_llm_config(request, payload: GlobalLLMConfigInSchema):
    config, created = GlobalLLMConfig.objects.update_or_create(
        name=payload.name, defaults={"value": payload.value}
    )
    return config


class TestLLMAuthResponseSchema(Schema):
    message: str = None
    error: str = None
    answer: str = None


@router.post("/test-llm-auth", response=TestLLMAuthResponseSchema)
def test_llm_auth(request):
    try:
        from django_llm_chat.chat import Chat
        from .models import GlobalLLMConfig

        # Fetch the model configuration
        try:
            config = GlobalLLMConfig.objects.get(
                name=GlobalLLMConfig.NameChoices.REASONING_LLM_MODEL
            )
            model_name = config.value
        except GlobalLLMConfig.DoesNotExist:
            return {
                "error": "REASONING_LLM_MODEL is not configured. Please run /test-llm-auth again after configuring."
            }

        chat = Chat.create()
        # Create a basic message to test the auth
        answer = chat.send_user_msg_to_llm(model_name, "Hi, how are you?")
        return {"message": "Success", "answer": str(answer)}
    except Exception as e:
        return {"error": str(e)}
