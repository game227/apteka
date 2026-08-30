from django.core.cache import cache


def site_stats(request):
    stats = cache.get("site_stats")
    if stats is None:
        from catalog.models import Drug
        from pharmacies.models import Pharmacy

        stats = {
            "stats_drug_count": Drug.objects.count(),
            "stats_pharmacy_count": Pharmacy.objects.count(),
        }
        cache.set("site_stats", stats, 60)
    return stats
