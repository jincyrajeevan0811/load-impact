from django import forms

from accounts.forms import BootstrapFormMixin

from .models import ContactMessage


class ContactForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ("name", "email", "phone", "subject", "message")
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}
