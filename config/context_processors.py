from django.core.cache import cache
from django.urls import reverse


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


def notification_badge(request):
    """Qo'ng'iroqcha ikonkasi uchun: dorixona xodimiga — kelgan (hal
    qilinmagan) xabarlar soni, oddiy foydalanuvchiga — o'zi yuborgan va
    hali javob kutayotgan xabarlar soni. Ikkalasi ham alohida
    'accounts:notifications' sahifasiga olib boradi (profil emas)."""
    if not request.user.is_authenticated:
        return {}
    from catalog.models import PriceDropAlert
    from pharmacies.models import ContactMessage

    if request.user.is_pharmacy_staff:
        count = ContactMessage.objects.filter(pharmacy=request.user.pharmacy, is_resolved=False).count()
    else:
        count = ContactMessage.objects.filter(sender=request.user, is_resolved=False).count()
        count += PriceDropAlert.objects.filter(user=request.user, is_read=False).count()
    return {"notification_count": count, "notification_url": reverse("accounts:notifications")}
