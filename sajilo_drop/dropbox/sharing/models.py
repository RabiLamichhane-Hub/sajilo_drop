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



import os


class SharedFile(models.Model):
    file = models.FileField(upload_to="shared_files/")
    ip_address = models.GenericIPAddressField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    @property
    def filename(self):
        if self.file and self.file.name:
            return os.path.basename(self.file.name)
        return ""

    @property
    def file_exists(self):
        try:
            return bool(self.file and self.file.storage.exists(self.file.name))
        except Exception:
            return False

    @property
    def formatted_size(self):
        try:
            if not self.file or not self.file.storage.exists(self.file.name):
                return ""
            bytes_size = self.file.size
            if bytes_size == 0:
                return "0 B"
            units = ['B', 'KB', 'MB', 'GB', 'TB']
            for unit in units:
                if bytes_size < 1024.0:
                    return f"{bytes_size:.1f} {unit}".replace(".0 ", " ")
                bytes_size /= 1024.0
            return f"{bytes_size:.1f} PB"
        except Exception:
            return ""

    def __str__(self):
        return self.filename or "SharedFile"

    class Meta:
        managed = True
