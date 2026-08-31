from django.conf import settings
from django.db import models


class PrescriptionScan(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="prescription_scans"
    )
    image = models.ImageField(upload_to="prescriptions/%Y/%m/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Skan #{self.pk} ({self.created_at:%Y-%m-%d})"

    def save(self, *args, **kwargs):
        if self.image and not self.image._committed:
            from config.image_utils import compress_image

            self.image = compress_image(self.image, max_dimension=1600, quality=88)
        super().save(*args, **kwargs)


class PrescriptionScanItem(models.Model):
    STATUS_CHOICES = [
        ("matched", "Aniq topildi"),
        ("needs_confirmation", "Tasdiqlash kerak"),
        ("not_found", "Topilmadi"),
    ]

    scan = models.ForeignKey(PrescriptionScan, on_delete=models.CASCADE, related_name="items")
    raw_text = models.CharField(max_length=255)
    matched_drug = models.ForeignKey(
        "catalog.Drug", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    confirmed_drug = models.ForeignKey(
        "catalog.Drug", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    confidence = models.FloatField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="not_found")

    def __str__(self):
        return self.raw_text
