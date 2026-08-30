from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_not_required
from django.urls import include, path
from django.views.static import serve

urlpatterns = [
    path("boshqaruv/", admin.site.urls),
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
