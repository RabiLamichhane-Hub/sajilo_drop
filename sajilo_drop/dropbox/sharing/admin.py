from django.contrib import admin
from .models import Message, JSONLDSchema, SharedFile

@admin.register(SharedFile)
class SharedFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'ip_address', 'uploaded_at')
    readonly_fields = ('uploaded_at',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('content_preview', 'message_id', 'created_at', 'updated_at')
    search_fields = ('content', 'message_id')
    readonly_fields = ('message_id', 'created_at', 'updated_at')

    def content_preview(self, obj):
        return obj.content[:60]
    content_preview.short_description = "Content"

admin.site.register(JSONLDSchema)
