from django.db import models


class Thread(models.Model):
    chat = models.ForeignKey(
        "django_llm_chat.Chat",
        on_delete=models.CASCADE,
        related_name="threads",
        help_text="The LLM chat session this thread belongs to"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Thread {self.pk} for Chat {self.chat_id}"


class Statement(models.Model):
    thread = models.ForeignKey(
        Thread,
        on_delete=models.CASCADE,
        related_name="statements",
        null=True,
        blank=True,
        help_text="The thread this statement was generated in"
    )
    content = models.TextField(help_text="The core content of the statement")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return str(self.content[:50])


class StatementRelationship(models.Model):
    source = models.ForeignKey(
        Statement,
        on_delete=models.CASCADE,
        related_name="source_relationships",
        help_text="The statement from which the relationship originates"
    )
    target = models.ForeignKey(
        Statement,
        on_delete=models.CASCADE,
        related_name="target_relationships",
        help_text="The statement to which the relationship points"
    )
    relationship_type = models.CharField(
        max_length=255,
        blank=True,
        help_text="The type or nature of the relationship (e.g., 'supports', 'contradicts')"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source", "target", "relationship_type"],
                name="unique_statement_relationship"
            )
        ]

    def __str__(self) -> str:
        return f"{self.source} -[{self.relationship_type}]-> {self.target}"
