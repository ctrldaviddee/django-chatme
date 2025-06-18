from django import forms
from django.forms import ModelForm

from .models import GroupMessages


class ChatMessageCreateForm(ModelForm):

    class Meta:
        model = GroupMessages
        fields = ["content"]
        widgets = {
            "content": forms.TextInput(
                attrs={
                    "placeholder": "Message ...",
                    "class": "p-4 text-black",
                    "maxlength": "300",
                    "autofocus": True,
                }
            )
        }
