from django.db import models
import uuid

# Create your models here.
class PublicMessage(models.Model):
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    ip = models.GenericIPAddressField(
        null=False,
        blank= False)
    
    content = models.TextField()
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.content[:50]