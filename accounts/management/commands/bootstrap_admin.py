import os

from django.core.management.base import BaseCommand

from accounts.models import User


class Command(BaseCommand):
    """Deploy'ning har bosqichida xavfsiz ishga tushiriladi: ADMIN_BOOTSTRAP_*
    muhit o'zgaruvchilari berilgan va hali birorta superuser yo'q bo'lsagina
    birinchi adminni yaratadi — aks holda hech narsa qilmaydi (idempotent)."""

    help = "ADMIN_BOOTSTRAP_USERNAME/PASSWORD/EMAIL berilgan bo'lsa va superuser mavjud bo'lmasa, birinchi adminni yaratadi."

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_BOOTSTRAP_USERNAME")
        password = os.environ.get("ADMIN_BOOTSTRAP_PASSWORD")
        email = os.environ.get("ADMIN_BOOTSTRAP_EMAIL", "")

        if not username or not password:
            self.stdout.write("ADMIN_BOOTSTRAP_USERNAME/PASSWORD berilmagan — o'tkazib yuborildi.")
            return

        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write("Superuser allaqachon mavjud — o'tkazib yuborildi.")
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' yaratildi."))
