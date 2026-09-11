from django.contrib import admin
from .models import PublicMessage

# Register your models here.

@admin.register(PublicMessage)
class PublicMessageAdmin(admin.ModelAdmin):
    list_display = ('content_preview', 'message_id', 'created_at', 'updated_at')
    search_fields = ('content', 'message_id')
    readonly_fields = ('message_id', 'created_at', 'updated_at')

    def content_preview(self, obj):
        return obj.content[:60]
    content_preview.short_description = "Content"