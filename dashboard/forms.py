from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from accounts.forms import BootstrapFormMixin, DateInput, TimeInput
from gym.models import (
    Announcement,
    Attendance,
    GymClass,
    Membership,
    MembershipPlan,
    Payment,
    Trainer,
)

User = get_user_model()


def member_choices():
    return User.objects.filter(is_active=True).order_by("first_name", "username")


class MemberUserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        name = obj.get_full_name() or obj.username
        return f"{name} (@{obj.username})"


# ---------- Members ----------
class MemberCreateForm(BootstrapFormMixin, UserCreationForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField()

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class MemberUpdateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "is_active", "is_staff")
        labels = {
            "is_active": "Account active (can log in)",
            "is_staff": "Staff / Admin access",
        }
        help_texts = {"is_staff": "Gives access to this admin dashboard.", "username": ""}

    def __init__(self, *args, **kwargs):
        self.editor = kwargs.pop("editor", None)
        super().__init__(*args, **kwargs)
        # Only superusers may grant or remove staff rights.
        if not (self.editor and self.editor.is_superuser):
            self.fields.pop("is_staff")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if email and User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Another account already uses this email.")
        return email


# ---------- Gym data ----------
class PlanForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = MembershipPlan
        fields = ("name", "duration_days", "price", "description", "features", "is_popular", "is_active")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
            "features": forms.Textarea(attrs={"rows": 5}),
        }


class TrainerForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Trainer
        fields = (
            "name", "gender", "specialization", "experience_years", "phone", "email",
            "instagram", "photo", "bio", "is_active",
        )
        widgets = {"bio": forms.Textarea(attrs={"rows": 3})}


class GymClassForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = GymClass
        fields = (
            "name", "trainer", "day_of_week", "start_time", "end_time", "capacity", "level",
            "location", "description", "is_active",
        )
        widgets = {
            "start_time": TimeInput(),
            "end_time": TimeInput(),
            "description": forms.Textarea(attrs={"rows": 2}),
        }

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("start_time"), cleaned.get("end_time")
        if start and end and end <= start:
            self.add_error("end_time", "End time must be after the start time.")
        return cleaned


class MembershipForm(BootstrapFormMixin, forms.ModelForm):
    user = MemberUserChoiceField(queryset=User.objects.none(), label="Member")
    record_payment = forms.BooleanField(
        required=False, initial=True, label="Also record a payment for this plan"
    )
    payment_method = forms.ChoiceField(choices=Payment.METHOD_CHOICES, required=False)
    payment_status = forms.ChoiceField(
        choices=Payment.STATUS_CHOICES, required=False, initial="paid"
    )

    class Meta:
        model = Membership
        fields = ("user", "plan", "status", "start_date", "end_date", "notes")
        widgets = {"start_date": DateInput(), "end_date": DateInput()}
        help_texts = {
            "start_date": "Leave empty to start today (or the day after the member's current plan ends).",
            "end_date": "Leave empty to calculate it from the plan duration.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = member_choices()
        self.fields["plan"].queryset = MembershipPlan.objects.all()
        if self.instance.pk:
            # The payment shortcut only makes sense when creating a membership.
            for name in ("record_payment", "payment_method", "payment_status"):
                self.fields.pop(name)

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("start_date"), cleaned.get("end_date")
        if start and end and end < start:
            self.add_error("end_date", "End date cannot be before the start date.")
        return cleaned


class PaymentForm(BootstrapFormMixin, forms.ModelForm):
    user = MemberUserChoiceField(queryset=User.objects.none(), label="Member")

    class Meta:
        model = Payment
        fields = ("user", "membership", "amount", "method", "status", "transaction_id", "notes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = member_choices()
        self.fields["membership"].queryset = Membership.objects.select_related("user", "plan")
        self.fields["membership"].required = False

    def clean(self):
        cleaned = super().clean()
        membership, user = cleaned.get("membership"), cleaned.get("user")
        if membership and user and membership.user_id != user.id:
            self.add_error("membership", "This membership belongs to a different member.")
        return cleaned


class CheckInForm(BootstrapFormMixin, forms.ModelForm):
    user = MemberUserChoiceField(queryset=User.objects.none(), label="Member")

    class Meta:
        model = Attendance
        fields = ("user", "date", "check_in", "check_out")
        widgets = {"date": DateInput(), "check_in": TimeInput(), "check_out": TimeInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = member_choices().filter(is_staff=False)
        if not self.instance.pk:
            now = timezone.localtime()
            self.fields["date"].initial = now.date()
            self.fields["check_in"].initial = now.strftime("%H:%M")


class AnnouncementForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ("title", "content", "is_active")
        widgets = {"content": forms.Textarea(attrs={"rows": 5})}
