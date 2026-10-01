from .models import Message, JSONLDSchema, SharedFile
from django import forms

class MessageForm(forms.ModelForm):
    
    class Meta:
        model = Message
        fields = ("content",)



class JSONLDSchemaForm(forms.ModelForm):
    class Meta:
        model = JSONLDSchema
        fields = ["name"]


class SharedFileForm(forms.ModelForm):
    class Meta:
        model = SharedFile
        fields = ["file"]