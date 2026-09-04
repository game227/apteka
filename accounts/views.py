import io
import time
from collections import Counter

import pyotp
import qrcode
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from accounts.forms import ProfileForm, RegisterForm, StyledAuthenticationForm, StyledPasswordResetForm
from accounts.models import User, UserRole
from accounts.tokens import email_verification_token
from catalog.models import Favorite, PriceDropAlert, SearchQuery
from pharmacies.models import ContactMessage, PharmacyInvite
from prescriptions.models import PrescriptionScan, PrescriptionScanItem


def _send_verification_email(request, user):
    """Ro'yxatdan o'tishda yoki qayta so'ralganda tasdiqlash havolasini
    yuboradi. SMTP sozlanmagan bo'lsa ham (fail_silently) ro'yxatdan
    o'tish jarayoni buzilmasin deb xatolik yutiladi."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)
    link = request.build_absolute_uri(reverse("accounts:verify_email", args=[uid, token]))
    body = render_to_string("accounts/verification_email.txt", {"user": user, "link": link})
    send_mail(
        "Dori Narxlari — emailni tasdiqlash",
        body,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True,
    )

LOGIN_ATTEMPT_LIMIT = 5
LOGIN_LOCKOUT_SECONDS = 15 * 60

REGISTER_ATTEMPT_LIMIT = 3
REGISTER_LOCKOUT_SECONDS = 60 * 60

PASSWORD_RESET_ATTEMPT_LIMIT = 5
PASSWORD_RESET_LOCKOUT_SECONDS = 60 * 60


def _login_attempts_key(request):
    return f"login_attempts:{request.META.get('REMOTE_ADDR', 'unknown')}"


def _register_attempts_key(request):
    return f"register_attempts:{request.META.get('REMOTE_ADDR', 'unknown')}"


def _password_reset_attempts_key(request):
    return f"pwreset_attempts:{request.META.get('REMOTE_ADDR', 'unknown')}"


@method_decorator(login_not_required, name="dispatch")
class AptekaLoginView(LoginView):
    """Brute-force'dan himoya: bitta IP'dan ketma-ket 5 marta noto'g'ri
    urinishdan keyin 15 daqiqaga login bloklanadi (Django cache orqali,
    qo'shimcha kutubxonasiz)."""

    template_name = "accounts/login.html"
    redirect_authenticated_user = True
    authentication_form = StyledAuthenticationForm

    def post(self, request, *args, **kwargs):
        if cache.get(_login_attempts_key(request), 0) >= LOGIN_ATTEMPT_LIMIT:
            messages.error(
                request,
                f"Juda ko'p noto'g'ri urinish. {LOGIN_LOCKOUT_SECONDS // 60} daqiqadan keyin qayta urinib ko'ring.",
            )
            return self.render_to_response(self.get_context_data())
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        key = _login_attempts_key(self.request)
        attempts = cache.get(key, 0) + 1
        cache.set(key, attempts, LOGIN_LOCKOUT_SECONDS)
        remaining = LOGIN_ATTEMPT_LIMIT - attempts
        if remaining > 0:
            messages.warning(self.request, f"Yana {remaining} ta urinish qoldi.")
        return super().form_invalid(form)

    def form_valid(self, form):
        cache.delete(_login_attempts_key(self.request))
        user = form.get_user()
        if user.totp_enabled:
            self.request.session["pre_2fa_user_id"] = user.pk
            return redirect("accounts:totp_verify")
        return super().form_valid(form)


TOTP_ATTEMPT_LIMIT = 5
TOTP_LOCKOUT_SECONDS = 15 * 60


def _totp_attempts_key(user_id):
    return f"totp_attempts:{user_id}"


@login_not_required
def totp_verify_view(request):
    """Parol to'g'ri kiritilgach, agar foydalanuvchida 2FA yoqilgan bo'lsa,
    shu oraliq bosqichda autentifikator ilovadagi 6 xonali kod so'raladi —
    kod to'g'ri bo'lgandagina haqiqiy login() chaqiriladi."""
    user_id = request.session.get("pre_2fa_user_id")
    if not user_id:
        return redirect("accounts:login")
    user = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        if cache.get(_totp_attempts_key(user_id), 0) >= TOTP_ATTEMPT_LIMIT:
            messages.error(
                request,
                f"Juda ko'p noto'g'ri urinish. {TOTP_LOCKOUT_SECONDS // 60} daqiqadan keyin qayta urinib ko'ring.",
            )
            return render(request, "accounts/totp_verify.html", {"debug": settings.DEBUG})

        code = (request.POST.get("code") or "").strip()
        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(code, valid_window=1):
            cache.delete(_totp_attempts_key(user_id))
            del request.session["pre_2fa_user_id"]
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, "Xush kelibsiz!")
            return redirect("catalog:home")

        attempts = cache.get(_totp_attempts_key(user_id), 0) + 1
        cache.set(_totp_attempts_key(user_id), attempts, TOTP_LOCKOUT_SECONDS)
        messages.error(request, "Kod noto'g'ri. Qayta urinib ko'ring.")

    return render(request, "accounts/totp_verify.html", {"debug": settings.DEBUG})


def totp_setup_view(request):
    user = request.user
    if user.totp_enabled:
        messages.info(request, "Ikki bosqichli autentifikatsiya allaqachon yoqilgan.")
        return redirect("accounts:profile")

    if not user.totp_secret:
        user.totp_secret = pyotp.random_base32()
        user.save(update_fields=["totp_secret"])

    if request.method == "POST":
        code = (request.POST.get("code") or "").strip()
        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(code, valid_window=1):
            user.totp_enabled = True
            user.save(update_fields=["totp_enabled"])
            messages.success(request, "Ikki bosqichli autentifikatsiya yoqildi!")
            return redirect("accounts:profile")
        messages.error(request, "Kod noto'g'ri. Autentifikator ilovadagi joriy 6 xonali kodni kiriting.")

    provisioning_uri = pyotp.TOTP(user.totp_secret).provisioning_uri(name=user.email or user.username, issuer_name="Dori Narxlari")
    return render(
        request,
        "accounts/totp_setup.html",
        {"secret": user.totp_secret, "provisioning_uri": provisioning_uri, "debug": settings.DEBUG},
    )


def totp_qr_view(request):
    """Joriy foydalanuvchining 2FA sozlash QR kodi — faqat o'zi ko'ra oladi
    (login talab qilinadi, tokensiz to'g'ridan-to'g'ri request.user'ga bog'liq)."""
    user = request.user
    if not user.totp_secret:
        return HttpResponse(status=404)
    uri = pyotp.TOTP(user.totp_secret).provisioning_uri(name=user.email or user.username, issuer_name="Dori Narxlari")
    img = qrcode.make(uri, box_size=8, border=2)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return HttpResponse(buf.getvalue(), content_type="image/png")


def _dev_simulator_user(request):
    """Simulyator qaysi hisobning kodini ko'rsatishi kerakligini aniqlaydi:
    2FA sozlash paytida — request.user, login'dagi tasdiqlash bosqichida —
    sessiyadagi kutilayotgan foydalanuvchi."""
    if request.user.is_authenticated and request.user.totp_secret:
        return request.user
    pending_id = request.session.get("pre_2fa_user_id")
    if pending_id:
        return User.objects.filter(pk=pending_id).first()
    return None


@login_not_required
def totp_simulator_view(request):
    """Faqat DEBUG (lokal) rejimda ishlaydi: haqiqiy telefon autentifikator
    ilovasini simulyatsiya qiluvchi alohida sahifa — asosiy sahifa (2FA
    sozlash yoki login tasdiqlash) bilan bir xil brauzerda ochilsa,
    BroadcastChannel orqali joriy kodni avtomatik uzatib turadi."""
    if not settings.DEBUG:
        return HttpResponse(status=404)
    if not _dev_simulator_user(request):
        return HttpResponse(status=404)
    return render(request, "accounts/totp_simulator.html")


@login_not_required
def totp_simulator_code_view(request):
    if not settings.DEBUG:
        return HttpResponse(status=404)
    user = _dev_simulator_user(request)
    if not user:
        return JsonResponse({"error": "no_secret"}, status=404)
    code = pyotp.TOTP(user.totp_secret).now()
    seconds_left = 30 - (int(time.time()) % 30)
    return JsonResponse({"code": code, "seconds_left": seconds_left})


def totp_disable_view(request):
    if request.method == "POST":
        password = request.POST.get("password") or ""
        if request.user.check_password(password):
            request.user.totp_enabled = False
            request.user.totp_secret = ""
            request.user.save(update_fields=["totp_enabled", "totp_secret"])
            messages.success(request, "Ikki bosqichli autentifikatsiya o'chirildi.")
        else:
            messages.error(request, "Parol noto'g'ri.")
    return redirect("accounts:profile")


@method_decorator(login_not_required, name="dispatch")
class RateLimitedPasswordResetView(auth_views.PasswordResetView):
    """Bitta IP'dan ketma-ket ko'p marta parol-tiklash so'rovi yuborib,
    email'ni bombardimon qilish yoki ro'yxatdagi manzillarni "tekshirib
    chiqish"ning oldini oladi — email mavjud yoki yo'qligidan qat'i nazar
    har bir POST urinish sifatida hisoblanadi."""

    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/password_reset_email.html"
    subject_template_name = "accounts/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")
    form_class = StyledPasswordResetForm

    def post(self, request, *args, **kwargs):
        key = _password_reset_attempts_key(request)
        attempts = cache.get(key, 0)
        if attempts >= PASSWORD_RESET_ATTEMPT_LIMIT:
            messages.error(
                request,
                f"Juda ko'p urinish. {PASSWORD_RESET_LOCKOUT_SECONDS // 60} daqiqadan keyin qayta urinib ko'ring.",
            )
            return redirect("accounts:password_reset")
        cache.set(key, attempts + 1, PASSWORD_RESET_LOCKOUT_SECONDS)
        return super().post(request, *args, **kwargs)


@login_not_required
def register_view(request):
    invite_token = request.GET.get("invite") or request.POST.get("invite_token")
    invite = None
    if invite_token:
        invite = PharmacyInvite.objects.filter(token=invite_token).first()
        if invite and not invite.is_valid:
            messages.warning(request, "Taklif havolasi muddati o'tgan yoki allaqachon ishlatilgan.")
            invite = None

    if request.method == "POST":
        register_key = _register_attempts_key(request)
        if cache.get(register_key, 0) >= REGISTER_ATTEMPT_LIMIT:
            messages.error(
                request,
                f"Bu manzildan juda ko'p hisob yaratildi. {REGISTER_LOCKOUT_SECONDS // 60} daqiqadan keyin qayta urinib ko'ring.",
            )
            form = RegisterForm()
            return render(request, "accounts/register.html", {"form": form, "invite": invite})

        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if invite:
                user.role = UserRole.PHARMACY_STAFF
                user.pharmacy = invite.pharmacy
            user.save()
            if invite:
                invite.used_by = user
                invite.save(update_fields=["used_by"])
            cache.set(register_key, cache.get(register_key, 0) + 1, REGISTER_LOCKOUT_SECONDS)
            login(request, user)
            _send_verification_email(request, user)
            messages.success(request, "Xush kelibsiz! Email manzilingizni tasdiqlash uchun sizga havola yubordik.")
            return redirect("catalog:home")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form, "invite": invite})


@login_not_required
def verify_email_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and email_verification_token.check_token(user, token):
        user.email_verified = True
        user.save(update_fields=["email_verified"])
        messages.success(request, "Email manzilingiz tasdiqlandi!")
    else:
        messages.error(request, "Tasdiqlash havolasi yaroqsiz yoki muddati o'tgan.")
    return redirect("catalog:home")


def resend_verification_email_view(request):
    if request.user.email_verified:
        messages.info(request, "Email manzilingiz allaqachon tasdiqlangan.")
    else:
        _send_verification_email(request, request.user)
        messages.success(request, "Tasdiqlash havolasi qayta yuborildi.")
    return redirect("accounts:profile")


def profile_view(request):
    if request.method == "POST":
        old_email = request.user.email
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            email_changed = form.cleaned_data["email"] != old_email
            user = form.save(commit=False)
            if email_changed:
                user.email_verified = False
            user.save()
            if email_changed:
                _send_verification_email(request, user)
                messages.success(request, "Profil yangilandi. Yangi email manzilingizni tasdiqlash uchun havola yubordik.")
            else:
                messages.success(request, "Profil yangilandi.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)

    all_favorites = list(
        Favorite.objects.filter(user=request.user).select_related("drug", "drug__substance", "drug__substance__category")
    )

    from pharmacies.services import nearby_prices

    monthly_cost = 0
    for fav in all_favorites:
        cheapest = nearby_prices(fav.drug_id, None, None)
        if cheapest:
            fav.cheapest_price = cheapest[0].price
            monthly_cost += float(cheapest[0].price)
        else:
            fav.cheapest_price = None

    search_count = SearchQuery.objects.filter(user=request.user).count()
    scan_count = PrescriptionScan.objects.filter(user=request.user).count()
    matched_count = PrescriptionScanItem.objects.filter(
        scan__user=request.user, status="matched"
    ).count()

    category_counts = Counter(
        fav.drug.substance.category.name_uz
        for fav in all_favorites
        if fav.drug.substance.category_id
    )
    top_category = category_counts.most_common(1)[0][0] if category_counts else None

    member_days = (timezone.now() - request.user.date_joined).days

    context = {
        "form": form,
        "favorites": all_favorites[:20],
        "recent_searches": SearchQuery.objects.filter(user=request.user)[:10],
        "scans": PrescriptionScan.objects.filter(user=request.user)[:10],
        "analytics": {
            "search_count": search_count,
            "favorite_count": len(all_favorites),
            "scan_count": scan_count,
            "matched_count": matched_count,
            "top_category": top_category,
            "member_days": member_days,
        },
        "monthly_cost": monthly_cost,
    }
    return render(request, "accounts/profile.html", context)


def notifications_view(request):
    """Qo'ng'iroqcha ikonkasi shu yerga olib keladi — profil'dan alohida,
    xabarlarga bag'ishlangan sahifa. Dorixona xodimiga — pharmacy'siga
    kelgan xabarlar (hal qilish tugmasi bilan), oddiy foydalanuvchiga — o'zi
    yuborgan xabarlar va ularning holati."""
    price_alerts = []
    if request.user.is_pharmacy_staff:
        received = ContactMessage.objects.filter(pharmacy=request.user.pharmacy).select_related("sender")[:30]
        sent = []
    else:
        received = []
        sent = ContactMessage.objects.filter(sender=request.user).select_related("pharmacy")[:30]
        price_alerts = list(
            PriceDropAlert.objects.filter(user=request.user).select_related("drug", "pharmacy")[:30]
        )
        PriceDropAlert.objects.filter(user=request.user, is_read=False).update(is_read=True)

    return render(request, "accounts/notifications.html", {"received": received, "sent": sent, "price_alerts": price_alerts})
