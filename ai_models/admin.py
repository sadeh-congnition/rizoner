from django.contrib import admin
from .models import LLMModel


@admin.register(LLMModel)
class LLMModelAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
