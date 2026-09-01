from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_not_required
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import include, path
from django.views.static import serve

from config.sitemaps import CategorySitemap, DrugSitemap, PharmacySitemap, StaticViewSitemap

_sitemaps = {
    "static": StaticViewSitemap,
    "drugs": DrugSitemap,
    "pharmacies": PharmacySitemap,
    "categories": CategorySitemap,
}


@login_not_required
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /boshqaruv/",
        "Disallow: /hisob/",
        "Disallow: /dorixona/panel/",
        "Disallow: /dorixona/admin-panel/",
        "Disallow: /retsept/",
        "Allow: /",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


urlpatterns = [
    path("boshqaruv/", admin.site.urls),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", login_not_required(sitemap), {"sitemaps": _sitemaps}, name="sitemap"),
    path("", include("catalog.urls")),
    path("dorixona/", include("pharmacies.urls")),
    path("retsept/", include("prescriptions.urls")),
    path("hisob/", include("accounts.urls")),
]

if settings.DEBUG:
    # Media fayllar (dori rasmlari, retsept skanlari) login talab qilinmasdan
    # ham ochilishi uchun (LoginRequiredMiddleware barcha view'larga ta'sir
    # qiladi — static/ esa runserver'ning o'z StaticFilesHandler'i orqali
    # middleware'dan chetlab o'tib xizmat qilinadi, shuning uchun bu yerda
    # faqat MEDIA_URL kerak).
    urlpatterns += [
        path(
            f"{settings.MEDIA_URL.strip('/')}/<path:path>",
            login_not_required(serve),
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]
