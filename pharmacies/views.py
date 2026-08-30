import csv
import io

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from accounts.decorators import pharmacy_staff_required, platform_admin_required
from accounts.models import User, UserRole
from catalog.models import Drug
from pharmacies.forms import CsvUploadForm, PharmacyForm, PharmacyReviewForm, PriceForm
from pharmacies.models import Pharmacy, PharmacyInvite
from pharmacies.services import upsert_price


def pharmacy_detail_view(request, slug):
    pharmacy = get_object_or_404(Pharmacy, slug=slug)
    prices = pharmacy.prices.select_related("drug", "drug__substance").order_by("drug__trade_name")
    reviews = pharmacy.reviews.select_related("user")[:20]

    review_form = None
    if request.user.is_authenticated:
        if request.method == "POST":
            review_form = PharmacyReviewForm(request.POST)
            if review_form.is_valid():
                review, _ = pharmacy.reviews.update_or_create(
                    user=request.user,
                    defaults={"rating": review_form.cleaned_data["rating"], "comment": review_form.cleaned_data["comment"]},
                )
                messages.success(request, "Sharh uchun rahmat!")
                return redirect("pharmacies:detail", slug=slug)
        else:
            review_form = PharmacyReviewForm()

    context = {"pharmacy": pharmacy, "prices": prices, "reviews": reviews, "review_form": review_form}
    return render(request, "pharmacies/detail.html", context)


@pharmacy_staff_required
def staff_panel_view(request):
    pharmacy = request.user.pharmacy
    prices = pharmacy.prices.select_related("drug", "drug__substance").order_by("drug__trade_name")
    context = {
        "pharmacy": pharmacy,
        "prices": prices,
        "price_form": PriceForm(),
        "csv_form": CsvUploadForm(),
    }
    return render(request, "pharmacies/staff_panel.html", context)


@pharmacy_staff_required
def staff_price_update_view(request):
    if request.method == "POST":
        form = PriceForm(request.POST)
        if form.is_valid():
            upsert_price(
                pharmacy=request.user.pharmacy,
                drug=form.cleaned_data["drug"],
                price=form.cleaned_data["price"],
                in_stock=form.cleaned_data["in_stock"],
                user=request.user,
            )
            messages.success(request, "Narx saqlandi.")
    return redirect("pharmacies:staff_panel")


@pharmacy_staff_required
def staff_csv_upload_view(request):
    imported = 0
    errors = []
    if request.method == "POST":
        form = CsvUploadForm(request.POST, request.FILES)
        if form.is_valid():
            raw = form.cleaned_data["file"].read().decode("utf-8-sig", errors="replace")
            reader = csv.DictReader(io.StringIO(raw))
            for row_number, row in enumerate(reader, start=2):
                try:
                    drug_id = (row.get("drug_id") or "").strip()
                    trade_name = (row.get("trade_name") or "").strip()
                    price = float((row.get("price") or "").strip())
                    if price <= 0:
                        raise ValueError("price musbat son bo'lishi kerak")
                    in_stock = (row.get("in_stock") or "true").strip().lower() in {"1", "true", "yes", "ha"}

                    drug = None
                    if drug_id:
                        drug = Drug.objects.filter(id=int(drug_id)).first()
                    elif trade_name:
                        drug = Drug.objects.filter(trade_name__iexact=trade_name).first()
                    if drug is None:
                        raise ValueError("dori topilmadi (drug_id yoki trade_name noto'g'ri)")

                    upsert_price(pharmacy=request.user.pharmacy, drug=drug, price=price, in_stock=in_stock, user=request.user)
                    imported += 1
                except Exception as exc:  # noqa: BLE001 - har bir qatorni alohida xato sifatida yig'amiz
                    errors.append(f"{row_number}-qator: {exc}")
            messages.success(request, f"{imported} ta qator saqlandi, {len(errors)} ta xato.")
            for err in errors[:10]:
                messages.error(request, err)

    return redirect("pharmacies:staff_panel")


@platform_admin_required
def admin_dashboard_view(request):
    context = {
        "pharmacies": Pharmacy.objects.all().order_by("-created_at")[:50],
        "invites": PharmacyInvite.objects.select_related("pharmacy", "used_by").order_by("-created_at")[:20],
        "stats": {
            "pharmacy_count": Pharmacy.objects.count(),
            "drug_count": Drug.objects.count(),
            "staff_count": User.objects.filter(role=UserRole.PHARMACY_STAFF).count(),
        },
    }
    return render(request, "pharmacies/admin_dashboard.html", context)


@platform_admin_required
def admin_pharmacy_create_view(request):
    if request.method == "POST":
        form = PharmacyForm(request.POST)
        if form.is_valid():
            pharmacy = form.save(commit=False)
            pharmacy.created_by = request.user
            pharmacy.save()
            messages.success(request, f"“{pharmacy.name}” qo'shildi.")
            return redirect("pharmacies:admin_dashboard")
    else:
        form = PharmacyForm()
    return render(request, "pharmacies/admin_pharmacy_form.html", {"form": form})


@platform_admin_required
def admin_invite_create_view(request, pharmacy_id):
    pharmacy = get_object_or_404(Pharmacy, pk=pharmacy_id)
    invite = PharmacyInvite.objects.create(pharmacy=pharmacy)
    url = request.build_absolute_uri(reverse("accounts:register") + f"?invite={invite.token}")
    messages.success(request, f"Taklif havolasi yaratildi: {url}")
    return redirect("pharmacies:admin_dashboard")
