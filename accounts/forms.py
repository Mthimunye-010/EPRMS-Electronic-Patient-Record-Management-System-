from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django_otp.forms import OTPAuthenticationForm
from django_otp.plugins.otp_totp.models import TOTPDevice

from .models import User


class StyledAuthenticationForm(OTPAuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control", "autofocus": True})
        self.fields["password"].widget.attrs.update({"class": "form-control"})
        self.fields["otp_token"].label = "Authenticator code"
        self.fields["otp_token"].widget = forms.TextInput(attrs={
            "class": "form-control",
            "autocomplete": "one-time-code",
            "inputmode": "numeric",
            "pattern": "[0-9]*",
        })
        self.fields.pop("otp_device", None)

    def _chosen_device(self, user):
        # This project provisions one confirmed TOTP device per staff account.
        # Selecting it server-side removes an unnecessary device dropdown and
        # prevents the browser from choosing a device belonging to another user.
        return TOTPDevice.objects.devices_for_user(user).filter(confirmed=True).order_by("pk").first()


class StaffCreationForm(UserCreationForm):
    """Used by administrators to create new staff accounts."""

    current_password = forms.CharField(
        label="Confirm your password",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
        help_text="Required to confirm this account change.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "employee_id",
            "role",
            "department",
            "phone_number",
        )

    def __init__(self, *args, actor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.actor = actor
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_current_password(self):
        password = self.cleaned_data["current_password"]
        if not self.actor or not self.actor.check_password(password):
            raise forms.ValidationError("Password confirmation failed.")
        return password


class StaffChangeForm(UserChangeForm):
    password = None  # Password changes handled via a separate flow.
    current_password = forms.CharField(
        label="Confirm your password",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
        help_text="Required to confirm this account change.",
    )

    class Meta(UserChangeForm.Meta):
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "employee_id",
            "role",
            "department",
            "phone_number",
            "is_active_staff",
        )

    def __init__(self, *args, actor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.actor = actor
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_current_password(self):
        password = self.cleaned_data["current_password"]
        if not self.actor or not self.actor.check_password(password):
            raise forms.ValidationError("Password confirmation failed.")
        return password
