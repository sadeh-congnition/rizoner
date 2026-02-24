from django.contrib import admin

from .models import GlobalLLMConfig


@admin.register(GlobalLLMConfig)
class GlobalLLMConfigAdmin(admin.ModelAdmin):
    list_display = ("name", "value")
    search_fields = ("name",)
