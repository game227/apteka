import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, UserCreationForm
from django.utils import timezone

from accounts.models import User
from config.form_utils import style_form


def _generate_username(email):
    """Username endi ro'yxatdan o'tishda so'ralmaydi — login email orqali
    ishlaydi (accounts.backends.EmailOrUsernameModelBackend), lekin User
    modelida username hali ham unique/majburiy maydon, shu sabab email'ning
    "@" dan oldingi qismidan avtomatik, ichki-ishlatiladigan qiymat yasaladi."""
    base = re.sub(r"[^a-z0-9]", "", email.split("@")[0].lower()) or "user"
    username = base
    i = 1
    while User.objects.filter(username=username).exists():
        i += 1
        username = f"{base}{i}"
    return username


class RegisterForm(UserCreationForm):
    """Telefon raqami va foydalanuvchi nomi bu yerda so'ralmaydi —
    ro'yxatdan o'tishni qisqartirish uchun ataylab olib tashlangan: telefon
    kerak bo'lsa profildan qo'shiladi, login esa email orqali ishlaydi."""

    first_name = forms.CharField(label="Ism", max_length=150, required=True)
    email = forms.EmailField(label="Email", required=True, help_text="Kirish va parolni tiklash shu manzil orqali amalga oshadi.")
    terms_accepted = forms.BooleanField(
        required=True,
        label="Foydalanish shartlariga roziman",
        error_messages={"required": "Davom etish uchun foydalanish shartlariga rozilik bildirishingiz kerak."},
    )

    class Meta:
        model = User
        fields = ["first_name", "email", "password1", "password2", "terms_accepted"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Bu email allaqachon ro'yxatdan o'tgan.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = _generate_username(user.email)
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
