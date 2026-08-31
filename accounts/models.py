from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    """Web orqali beriladigan rollar. "Admin" bu ro'yxatda yo'q — u faqat
    Django superuser (createsuperuser, serverdan) sifatida mavjud bo'ladi,
    web orqali hech kim boshqasini admin qila olmaydi."""

    USER = "user", "Foydalanuvchi"
    PHARMACY_STAFF = "pharmacy_staff", "Dorixona xodimi"


class User(AbstractUser):
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.USER)
    phone = models.CharField(max_length=32, blank=True)
    accepted_terms_at = models.DateTimeField(null=True, blank=True)
    pharmacy = models.ForeignKey(
        "pharmacies.Pharmacy",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="staff_members",
    )

    @property
    def is_pharmacy_staff(self):
        return self.role == UserRole.PHARMACY_STAFF and self.pharmacy_id is not None

    @property
    def is_platform_admin(self):
        """Faqat serverdan yaratilgan superuser'lar admin hisoblanadi."""
        return self.is_superuser
