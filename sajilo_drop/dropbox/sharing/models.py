from django.db import models
import uuid
from django.core.exceptions import ValidationError

# Create your models here.
class Message(models.Model):
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    ip = models.GenericIPAddressField()


    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.secret_msg and not self.passkey:
            raise ValidationError({
                'passkey': 'Passkey is required for secret messages.'
            })

        if not self.secret_msg and self.passkey:
            raise ValidationError({
                'passkey': 'Passkey is not allowed for public messages.'
            })

    def __str__(self):
        return self.content[:50]



class JSONLDSchema(models.Model):
    name = models.CharField(max_length=255)
    schema = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name