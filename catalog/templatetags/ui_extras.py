"""Kichik, izchil ikonka to'plami — tashqi ikon kutubxonasiga bog'liq
bo'lmasdan (CSP/CDN'siz), oddiy SVG primitivlar orqali. Har bir shablonda
qo'lda SVG yozish o'rniga: {% icon 'heart' 'w-5 h-5' %}"""

from django import template
from django.utils import timezone
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def uz_timesince(value):
    """Django'ning ichki timesince/naturaltime filtrlari inglizcha chiqadi
    (o'zbekcha tarjima katalogi yo'q) — shu sabab narx qachon yangilanganini
    foydalanuvchiga ko'rsatish uchun o'zimizning oddiy o'zbekcha versiyasi."""
    if not value:
        return ""
    delta = timezone.now() - value
    seconds = delta.total_seconds()
    if seconds < 60:
        return "hozirgina"
    minutes = int(seconds // 60)
    if minutes < 60:
        return f"{minutes} daqiqa oldin"
    hours = int(seconds // 3600)
    if hours < 24:
        return f"{hours} soat oldin"
    days = int(seconds // 86400)
    if days < 30:
        return f"{days} kun oldin"
    months = int(days // 30)
    if months < 12:
        return f"{months} oy oldin"
    years = int(days // 365)
    return f"{years} yil oldin"


@register.filter
def is_price_stale(value, days=30):
    """Narx shu necha kundan beri yangilanmagan bo'lsa True — ro'yxatda
    "eskirgan bo'lishi mumkin" belgisini ko'rsatish uchun."""
    if not value:
        return False
    return (timezone.now() - value).days >= days

_ICONS = {
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><line x1="20" y1="20" x2="15.3" y2="15.3"/>',
    "camera": '<path d="M4 8h3l1.5-2h7L17 8h3a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z"/><circle cx="12" cy="13" r="3.5"/>',
    "heart": '<path d="M12 20.5s-7.5-4.6-9.8-9.3C.6 7.7 2.1 4.5 5.4 4c2-.3 3.8.7 4.6 2.3C10.8 4.7 12.6 3.7 14.6 4c3.3.5 4.8 3.7 3.2 7.2C15.5 15.9 12 20.5 12 20.5z"/>',
    "heart-solid": '<path fill="currentColor" stroke="none" d="M12 20.5s-7.5-4.6-9.8-9.3C.6 7.7 2.1 4.5 5.4 4c2-.3 3.8.7 4.6 2.3C10.8 4.7 12.6 3.7 14.6 4c3.3.5 4.8 3.7 3.2 7.2C15.5 15.9 12 20.5 12 20.5z"/>',
    "building": '<rect x="5" y="3" width="14" height="18" rx="1"/><line x1="9" y1="7" x2="9" y2="7.01"/><line x1="15" y1="7" x2="15" y2="7.01"/><line x1="9" y1="11" x2="9" y2="11.01"/><line x1="15" y1="11" x2="15" y2="11.01"/><line x1="9" y1="15" x2="9" y2="15.01"/><line x1="15" y1="15" x2="15" y2="15.01"/><path d="M10 21v-3a2 2 0 0 1 4 0v3"/>',
    "chart": '<line x1="5" y1="20" x2="5" y2="12"/><line x1="12" y1="20" x2="12" y2="6"/><line x1="19" y1="20" x2="19" y2="15"/><line x1="3" y1="20" x2="21" y2="20"/>',
    "user": '<circle cx="12" cy="8" r="3.5"/><path d="M5 20c0-3.9 3.1-7 7-7s7 3.1 7 7"/>',
    "logout": '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>',
    "star": '<path d="M12 3.5l2.6 5.4 5.9.8-4.3 4.2 1 5.9-5.2-2.8-5.2 2.8 1-5.9-4.3-4.2 5.9-.8z"/>',
    "star-solid": '<path fill="currentColor" stroke="none" d="M12 3.5l2.6 5.4 5.9.8-4.3 4.2 1 5.9-5.2-2.8-5.2 2.8 1-5.9-4.3-4.2 5.9-.8z"/>',
    "check-circle": '<circle cx="12" cy="12" r="9"/><polyline points="8.5 12.5 11 15 16 9"/>',
    "warning": '<path d="M12 3.5 21.5 20h-19z"/><line x1="12" y1="9.5" x2="12" y2="14"/><line x1="12" y1="16.5" x2="12" y2="16.51"/>',
    "map-pin": '<path d="M12 21s-6.5-5.6-6.5-11a6.5 6.5 0 0 1 13 0c0 5.4-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/>',
    "phone": '<path d="M6.5 3h3l1.5 5-2.3 1.8a13 13 0 0 0 5.5 5.5L15.5 13l5 1.5v3a2 2 0 0 1-2.2 2C10.5 18.8 5.2 13.5 4.5 5.7A2 2 0 0 1 6.5 3z"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15.5 14"/>',
    "plus": '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
    "menu": '<line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/>',
    "close": '<line x1="6" y1="6" x2="18" y2="18"/><line x1="6" y1="18" x2="18" y2="6"/>',
    "chevron-right": '<polyline points="9 6 15 12 9 18"/>',
    "arrow-right": '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="13 6 19 12 13 18"/>',
    "link": '<path d="M9 15l6-6"/><path d="M10 6l1-1a4 4 0 0 1 5.7 5.7l-1 1"/><path d="M14 18l-1 1A4 4 0 0 1 7.3 13.3l1-1"/>',
    "upload": '<path d="M12 16V4"/><polyline points="7 8.5 12 3.5 17 8.5"/><path d="M4 16v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3"/>',
    "pill": '<rect x="3" y="9" width="18" height="6" rx="3" transform="rotate(-45 12 12)"/><line x1="12" y1="7.8" x2="12" y2="16.2" transform="rotate(-45 12 12)"/>',
    "copy": '<rect x="9" y="9" width="11" height="11" rx="1.5"/><path d="M5 15H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v1"/>',
    "shield": '<path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6z"/>',
    "edit": '<path d="M4 20l1-4.2L15.8 5A2 2 0 0 1 18.6 5l.4.4A2 2 0 0 1 19 8.2L8.2 19z"/><line x1="13.5" y1="6.5" x2="17.5" y2="10.5"/>',
    "trash": '<path d="M5 7h14"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M6 7l1 13a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1l1-13"/><path d="M9 7V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v3"/>',
    "bell": '<path d="M6 8a6 6 0 0 1 12 0c0 4.5 1.5 6 2 6.5H4c.5-.5 2-2 2-6.5z"/><path d="M9.5 17a2.5 2.5 0 0 0 5 0"/>',
    "sun": '<circle cx="12" cy="12" r="4.5"/><path d="M12 2.5v2.5M12 19v2.5M4.2 4.2l1.8 1.8M18 18l1.8 1.8M2.5 12H5M19 12h2.5M4.2 19.8L6 18M18 6l1.8-1.8"/>',
    "moon": '<path d="M20 14.5A8.5 8.5 0 1 1 9.5 4a7 7 0 0 0 10.5 10.5z"/>',
    # Turkum belgilari — emoji o'rniga (izchillik va har xil qurilmada
    # bir xil ko'rinishi uchun).
    "thermometer": '<path d="M12 2.5a2.3 2.3 0 0 0-2.3 2.3v9.4a4 4 0 1 0 4.6 0V4.8A2.3 2.3 0 0 0 12 2.5z"/><line x1="12" y1="7" x2="12" y2="14.5"/><circle cx="12" cy="17" r="1.4" fill="currentColor" stroke="none"/>',
    "virus": '<circle cx="12" cy="12" r="4.5"/><line x1="12" y1="2.5" x2="12" y2="5"/><line x1="12" y1="19" x2="12" y2="21.5"/><line x1="2.5" y1="12" x2="5" y2="12"/><line x1="19" y1="12" x2="21.5" y2="12"/><line x1="5.5" y1="5.5" x2="7.2" y2="7.2"/><line x1="16.8" y1="16.8" x2="18.5" y2="18.5"/><line x1="5.5" y1="18.5" x2="7.2" y2="16.8"/><line x1="16.8" y1="7.2" x2="18.5" y2="5.5"/>',
    "droplet": '<path d="M12 2.8s-6.5 7.4-6.5 11.7a6.5 6.5 0 0 0 13 0C18.5 10.2 12 2.8 12 2.8z"/>',
    "flower": '<circle cx="12" cy="12" r="2.3"/><circle cx="12" cy="5.5" r="2.3"/><circle cx="12" cy="18.5" r="2.3"/><circle cx="5.5" cy="12" r="2.3"/><circle cx="18.5" cy="12" r="2.3"/>',
    "stomach": '<circle cx="12" cy="12" r="8.5"/><path d="M7.5 12c1.3-2 3-2 4.5 0s3.2 2 4.5 0"/>',
    "lungs": '<path d="M11 4v7.5c0 1-.6 1.5-1.4 2.2l-2.4 2c-1.2 1-1.7 2-1.7 3.6a1.7 1.7 0 0 0 3.4 0v-1.8"/><path d="M13 4v7.5c0 1 .6 1.5 1.4 2.2l2.4 2c1.2 1 1.7 2 1.7 3.6a1.7 1.7 0 0 1-3.4 0v-1.8"/><path d="M11 6.5c-1.5-1.5-4-1.5-4 1.5"/><path d="M13 6.5c1.5-1.5 4-1.5 4 1.5"/>',
    "bottle": '<path d="M9.5 2.5h5v3.2l1.5 2.3v11.5a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2V8l1.5-2.3z"/><line x1="9" y1="11" x2="15" y2="11"/>',
    "grid": '<rect x="3" y="3" width="8" height="8" rx="1.5"/><rect x="13" y="3" width="8" height="8" rx="1.5"/><rect x="3" y="13" width="8" height="8" rx="1.5"/><rect x="13" y="13" width="8" height="8" rx="1.5"/>',
}


@register.simple_tag
def icon(name, css_class="w-5 h-5", stroke_width="1.8"):
    inner = _ICONS.get(name, "")
    svg = (
        f'<svg class="{css_class}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="{stroke_width}" '
        f'stroke-linecap="round" stroke-linejoin="round">{inner}</svg>'
    )
    return mark_safe(svg)
