from django import forms

from accounts.forms import BootstrapFormMixin
from gym.models import Payment


class SubscribeForm(BootstrapFormMixin, forms.Form):
    method = forms.ChoiceField(label="Payment method", choices=Payment.METHOD_CHOICES)
    transaction_id = forms.CharField(
        label="Transaction / UPI reference no.",
        max_length=100,
        required=False,
        help_text="Required for UPI, card and bank transfer payments.",
    )
    notes = forms.CharField(label="Note for the front desk (optional)", max_length=255, required=False)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("method") in ("upi", "card", "bank") and not cleaned.get("transaction_id"):
            self.add_error("transaction_id", "Please enter the transaction reference for online payments.")
        return cleaned
