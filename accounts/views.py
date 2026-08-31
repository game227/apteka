from collections import Counter

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator

from accounts.forms import ProfileForm, RegisterForm, StyledAuthenticationForm
from accounts.models import UserRole
from catalog.models import Favorite, SearchQuery
from pharmacies.models import ContactMessage, PharmacyInvite
from prescriptions.models import PrescriptionScan, PrescriptionScanItem

LOGIN_ATTEMPT_LIMIT = 5
LOGIN_LOCKOUT_SECONDS = 15 * 60


def _login_attempts_key(request):
    return f"login_attempts:{request.META.get('REMOTE_ADDR', 'unknown')}"


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
        return super().form_valid(form)


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
            login(request, user)
            messages.success(request, "Xush kelibsiz!")
            return redirect("catalog:home")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form, "invite": invite})


def profile_view(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil yangilandi.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)

    all_favorites = list(
        Favorite.objects.filter(user=request.user).select_related("drug", "drug__substance", "drug__substance__category")
    )
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
    }
    return render(request, "accounts/profile.html", context)


def notifications_view(request):
    """Qo'ng'iroqcha ikonkasi shu yerga olib keladi — profil'dan alohida,
    xabarlarga bag'ishlangan sahifa. Dorixona xodimiga — pharmacy'siga
    kelgan xabarlar (hal qilish tugmasi bilan), oddiy foydalanuvchiga — o'zi
    yuborgan xabarlar va ularning holati."""
    if request.user.is_pharmacy_staff:
        received = ContactMessage.objects.filter(pharmacy=request.user.pharmacy).select_related("sender")[:30]
        sent = []
    else:
        received = []
        sent = ContactMessage.objects.filter(sender=request.user).select_related("pharmacy")[:30]

    return render(request, "accounts/notifications.html", {"received": received, "sent": sent})
