import secrets
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


def _invite_expiry():
    return timezone.now() + timedelta(days=7)


class Pharmacy(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    address = models.CharField(max_length=500)
    lat = models.FloatField()
    lng = models.FloatField()
    phone = models.CharField(max_length=50, blank=True)
    work_hours = models.CharField(max_length=100, blank=True, default="09:00–21:00")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_pharmacies"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Pharmacies"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "dorixona"
            slug = base
            i = 1
            while Pharmacy.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("pharmacies:detail", args=[self.slug])

    @property
    def average_rating(self):
        agg = self.reviews.aggregate(models.Avg("rating"))
        return agg["rating__avg"]


class PharmacyDrugPrice(models.Model):
    """Bitta (pharmacy, drug) juftligi uchun joriy narx — upsert-only."""

    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name="prices")
    drug = models.ForeignKey("catalog.Drug", on_delete=models.CASCADE, related_name="prices")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="price_updates"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("pharmacy", "drug")]
        ordering = ["price"]

    def __str__(self):
        return f"{self.pharmacy} · {self.drug} = {self.price}"

    @property
    def deviation_pct(self):
        ref = self.drug.reference_price
        if not ref:
            return None
        return round(float((self.price - ref) / ref) * 100, 1)

    @property
    def is_overpriced(self):
        dev = self.deviation_pct
        return dev is not None and dev > settings.PRICE_DEVIATION_THRESHOLD * 100


class PriceHistory(models.Model):
    """Append-only: har bir narx o'zgarishida yangi yozuv qo'shiladi."""

    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name="price_history")
    drug = models.ForeignKey("catalog.Drug", on_delete=models.CASCADE, related_name="price_history")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]
        verbose_name_plural = "Price history"


class PharmacyInvite(models.Model):
    """Admin bir martalik taklif havolasini yaratadi, xodim shu orqali ro'yxatdan o'tadi."""

    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name="invites")
    token = models.CharField(max_length=64, unique=True, default=secrets.token_urlsafe, editable=False)
    used_by = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="used_invite"
    )
    expires_at = models.DateTimeField(default=_invite_expiry)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pharmacy} — {self.token[:10]}…"

    @property
    def is_valid(self):
        return self.used_by_id is None and self.expires_at > timezone.now()


class PharmacyReview(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pharmacy_reviews")
    rating = models.PositiveSmallIntegerField()
    comment = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("pharmacy", "user")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.pharmacy} — {self.rating}★"
