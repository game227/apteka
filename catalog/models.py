from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name_uz = models.CharField(max_length=120)
    name_ru = models.CharField(max_length=120, blank=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    icon = models.CharField(max_length=8, blank=True, help_text="Emoji, masalan 💊")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name_uz"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name_uz

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_uz)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:category", args=[self.slug])


class Substance(models.Model):
    """Ta'sir moddasi / INN."""

    name_inn = models.CharField("INN nomi", max_length=255, db_index=True)
    name_uz = models.CharField(max_length=255, blank=True)
    name_ru = models.CharField(max_length=255, blank=True)
    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL, related_name="substances"
    )

    class Meta:
        ordering = ["name_inn"]

    def __str__(self):
        return self.name_inn


class Drug(models.Model):
    """Savdo nomi (bitta substance ostida bir nechta bo'lishi mumkin)."""

    trade_name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    substance = models.ForeignKey(Substance, on_delete=models.PROTECT, related_name="drugs")
    manufacturer = models.CharField(max_length=255, blank=True)
    dosage_form = models.CharField(max_length=100, blank=True)
    dosage_strength = models.CharField(max_length=100, blank=True)
    reference_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to="drugs/", null=True, blank=True)
    search_hits = models.PositiveIntegerField(default=0, help_text="Nechta marta qidiruv/ko'rish natijasida ochilgan")

    class Meta:
        ordering = ["trade_name"]

    def __str__(self):
        return f"{self.trade_name} ({self.dosage_strength})" if self.dosage_strength else self.trade_name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.trade_name}-{self.dosage_strength}") or slugify(self.trade_name)
            slug = base
            i = 1
            while Drug.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug
        if self.image and not self.image._committed:
            from config.image_utils import compress_image

            self.image = compress_image(self.image, max_dimension=800)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:drug_detail", args=[self.slug])


class DrugAlias(models.Model):
    """Normalizatsiya uchun: turli yozilishlar (lotin/kirill/xato)."""

    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, related_name="aliases")
    alias_text = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return self.alias_text


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites")
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "drug")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} ♥ {self.drug}"


class SearchQuery(models.Model):
    """Qidiruv tarixi — 'oxirgi qidiruvlar' va ommabop dorilar tahlili uchun."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="search_queries"
    )
    query_text = models.CharField(max_length=255)
    result_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Search queries"

    def __str__(self):
        return self.query_text
