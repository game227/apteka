"""Kichik, izchil ikonka to'plami — tashqi ikon kutubxonasiga bog'liq
bo'lmasdan (CSP/CDN'siz), oddiy SVG primitivlar orqali. Har bir shablonda
qo'lda SVG yozish o'rniga: {% icon 'heart' 'w-5 h-5' %}"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

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
