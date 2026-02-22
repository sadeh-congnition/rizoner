from django.shortcuts import get_object_or_404
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
        name=payload.name,
        defaults={"value": payload.value}
    )
    return config
