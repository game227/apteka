from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from catalog.models import Category, Drug
from pharmacies.models import Pharmacy


class DrugSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Drug.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()


class PharmacySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Pharmacy.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()


class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()


class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ["catalog:home", "catalog:category_list", "catalog:about", "catalog:terms", "pharmacies:list"]

    def location(self, item):
        return reverse(item)
