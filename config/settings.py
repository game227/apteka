import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-key")
DEBUG = os.environ.get("DEBUG", "True") == "True"
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "*").split(",") if h.strip()]
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]

# Railway domenini avtomatik qo'shish — ALLOWED_HOSTS/CSRF_TRUSTED_ORIGINS'ni
# qo'lda sozlashni unutib qo'yish (va shu bilan 400 xatosi) oldini oladi.
_railway_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
if _railway_domain:
    ALLOWED_HOSTS.append(_railway_domain)
    CSRF_TRUSTED_ORIGINS.append(f"https://{_railway_domain}")

# SENTRY_DSN berilmasa hech narsa qilinmaydi (lokal dev'da kerak emas).
_sentry_dsn = os.environ.get("SENTRY_DSN")
if _sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=_sentry_dsn,
        integrations=[DjangoIntegration()],
        traces_sample_rate=float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        send_default_pii=False,
        environment=os.environ.get("SENTRY_ENVIRONMENT", "production" if not DEBUG else "development"),
    )

# Production'da (DEBUG=False) HTTPS va cookie xavfsizligini qattiqlashtiradi.
# Lokal dev'da (oddiy http://localhost) bu majburiy HTTPS'ga aylanib
# ishlashni buzmasligi uchun faqat DEBUG=False bo'lganda yoqiladi.
# Render (va shunga o'xshash) proxy orqasida ishlaganda so'rov aslida
# HTTPS orqali kelganini SECURE_PROXY_SSL_HEADER orqali bilib oladi.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 7  # 1 hafta — muammo bo'lmasa keyin oshirish mumkin
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.sitemaps",
    "accounts",
    "catalog",
    "pharmacies",
    "prescriptions",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "config.context_processors.site_stats",
                "config.context_processors.notification_badge",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Railway (va boshqa ko'p PaaS'lar) bitta DATABASE_URL o'zgaruvchisini beradi;
# u bo'lmasa (masalan lokal ishlab chiqishda) alohida POSTGRES_* o'zgaruvchilariga qaytadi.
if os.environ.get("DATABASE_URL"):
    import dj_database_url

    DATABASES = {"default": dj_database_url.parse(os.environ["DATABASE_URL"], conn_max_age=600)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "apteka_db"),
            "USER": os.environ.get("POSTGRES_USER", "neo"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "neo"),
            "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT", "5433"),
        }
    }

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
]

LANGUAGE_CODE = "uz"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# CLOUDINARY_URL berilsa (masalan "cloudinary://<key>:<secret>@<cloud_name>",
# Cloudinary boshqaruv panelidan to'g'ridan-to'g'ri nusxalanadi), yuklangan
# dori/retsept rasmlari u yerda doimiy saqlanadi — aks holda mahalliy disk
# ishlatiladi (Render bepul rejasida disk vaqtinchalik: har qayta
# joylashtirishda o'chib ketadi, shu sabab bu productionda MAJBURIY).
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
if os.environ.get("CLOUDINARY_URL"):
    STORAGES["default"] = {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"}

# Ba'zi uchinchi tomon paketlari hali ham eski STATICFILES_STORAGE
# sozlamasini to'g'ridan-to'g'ri tekshiradi (yangi STORAGES lug'atini emas) —
# ikkalasini mos saqlash uchun.
STATICFILES_STORAGE = STORAGES["staticfiles"]["BACKEND"]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "catalog:home"
LOGOUT_REDIRECT_URL = "catalog:home"

# EMAIL_HOST berilsa avtomatik SMTP orqali yuboriladi (masalan Gmail/SendGrid),
# aks holda email konsolga chiqadi (lokal ishlab chiqish uchun standart holat).
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend" if os.environ.get("EMAIL_HOST") else "django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@dorinarxlari.local")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# ADMIN_ALERT_EMAIL berilsa (yoki ADMIN_BOOTSTRAP_EMAIL'dan olinsa), Django
# serverda kutilmagan xatolik (500) yuz berganda shu manzilga avtomatik
# email yuboradi — Sentry hali ulanmagan bo'lsa ham, hech bo'lmaganda
# xatolik yuz berganini bilib turish uchun (EMAIL_HOST sozlangan bo'lishi kerak).
_admin_alert_email = os.environ.get("ADMIN_ALERT_EMAIL") or os.environ.get("ADMIN_BOOTSTRAP_EMAIL")
if _admin_alert_email:
    ADMINS = [("Admin", _admin_alert_email)]
    MANAGERS = ADMINS

# --- Ilova sozlamalari ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
PRICE_DEVIATION_THRESHOLD = float(os.environ.get("PRICE_DEVIATION_THRESHOLD", "0.20"))
FUZZY_MATCH_THRESHOLD = int(os.environ.get("FUZZY_MATCH_THRESHOLD", "80"))
FUZZY_MATCH_CONFIRM_THRESHOLD = int(os.environ.get("FUZZY_MATCH_CONFIRM_THRESHOLD", "60"))
