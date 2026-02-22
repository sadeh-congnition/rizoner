from django.db import models


class GlobalLLMConfig(models.Model):
    class NameChoices(models.TextChoices):
        TOOL_CALLING_LLM_MODEL = "tool_calling_llm_model", "Tool Calling LLM Model"
        REASONING_LLM_MODEL = "reasoning_llm_model", "Reasoning LLM Model"
        RESEARCH_LLM_MODEL = "research_llm_model", "Research LLM Model"

    name = models.CharField(
        max_length=255,
        choices=NameChoices.choices,
        unique=True,
        help_text="Name of the global configuration"
    )
    value = models.TextField(help_text="Value for the configuration item")

    class Meta:
        verbose_name = "Global LLM Configuration"
        verbose_name_plural = "Global LLM Configurations"

    def __str__(self) -> str:
        return str(self.get_name_display())
