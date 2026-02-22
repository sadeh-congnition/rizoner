from django.contrib import admin

from .models import Log, Statement, StatementRelationship, Thread


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ("id", "chat", "created_at", "updated_at")
    search_fields = ("chat__id",)
    list_filter = ("created_at", "updated_at")


@admin.register(Statement)
class StatementAdmin(admin.ModelAdmin):
    list_display = ("id", "content_preview", "thread", "created_at", "updated_at")
    search_fields = ("content",)
    list_filter = ("created_at", "updated_at", "thread")

    def content_preview(self, obj: Statement) -> str:
        return str(obj.content[:50])

    content_preview.short_description = "Content"


@admin.register(StatementRelationship)
class StatementRelationshipAdmin(admin.ModelAdmin):
    list_display = ("id", "source", "target", "relationship_type", "created_at")
    search_fields = ("source__content", "target__content", "relationship_type")
    list_filter = ("relationship_type", "created_at")


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ("id", "thread", "created_at")
    search_fields = ("thread__id",)
    list_filter = ("created_at", "thread")
