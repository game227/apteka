from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator

from accounts.forms import ProfileForm, RegisterForm, StyledAuthenticationForm
from accounts.models import UserRole
from catalog.models import Favorite, SearchQuery
from pharmacies.models import PharmacyInvite
from prescriptions.models import PrescriptionScan


@method_decorator(login_not_required, name="dispatch")
class AptekaLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True
    authentication_form = StyledAuthenticationForm


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

    context = {
        "form": form,
        "favorites": Favorite.objects.filter(user=request.user).select_related("drug", "drug__substance")[:20],
        "recent_searches": SearchQuery.objects.filter(user=request.user)[:10],
        "scans": PrescriptionScan.objects.filter(user=request.user)[:10],
    }
    return render(request, "accounts/profile.html", context)
