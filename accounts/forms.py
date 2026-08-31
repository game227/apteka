from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, UserCreationForm
from django.utils import timezone

from accounts.models import User
from config.form_utils import style_form


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label="Ism", max_length=150, required=True)
    email = forms.EmailField(label="Email", required=True, help_text="Parolni unutsangiz shu manzilga tiklash havolasi yuboriladi.")
    phone = forms.CharField(label="Telefon", max_length=32, required=False)
    terms_accepted = forms.BooleanField(
        required=True,
        label="Foydalanish shartlariga roziman",
        error_messages={"required": "Davom etish uchun foydalanish shartlariga rozilik bildirishingiz kerak."},
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "email", "phone", "password1", "password2", "terms_accepted"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.phone = self.cleaned_data.get("phone", "")
        user.accepted_terms_at = timezone.now()
        if commit:
            user.save()
        return user


class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)


class StyledPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)


class StyledSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)
