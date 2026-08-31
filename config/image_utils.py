"""Yuklangan rasmlarni saqlashdan oldin siqish — disk hajmi va sahifa
yuklanish tezligi uchun (dori rasmlari, retsept skanlari)."""

import io

from django.core.files.base import ContentFile
from PIL import Image


def compress_image(uploaded_file, max_dimension=1600, quality=85):
    """Rasmni belgilangan o'lchamgacha kichraytiradi va JPEG sifatida
    qayta siqadi. Natija asl fayl bilan bir xil interfeysga ega (ImageField'ga
    to'g'ridan-to'g'ri biriktiriladigan ContentFile)."""
    image = Image.open(uploaded_file)
    if image.mode in ("RGBA", "P", "LA"):
        image = image.convert("RGB")
    image.thumbnail((max_dimension, max_dimension), Image.LANCZOS)

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality, optimize=True)
    buffer.seek(0)

    base_name = uploaded_file.name.rsplit(".", 1)[0]
    return ContentFile(buffer.read(), name=f"{base_name}.jpg")
