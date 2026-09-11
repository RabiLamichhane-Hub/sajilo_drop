from .models import PublicMessage
from django import forms

class PublicMessageForm(forms.ModelForm):
    
    class Meta:
        model = PublicMessage
        fields = ("content",)
