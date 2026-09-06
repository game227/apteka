from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailOrUsernameModelBackend(ModelBackend):
    """Foydalanuvchi nomi (eski hisoblar uchun) yoki email orqali kirishga
    ruxsat beradi — ro'yxatdan o'tishda username so'ralmagani uchun,
    foydalanuvchi login sahifasida o'zi biladigan email'ni kiritadi."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email__iexact=username)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
