import csv
import io

import qrcode
from django.contrib import messages
from django.contrib.auth.decorators import login_not_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from accounts.decorators import pharmacy_staff_required, platform_admin_required
from accounts.models import User, UserRole
from catalog.models import Drug
from pharmacies.forms import (
    ContactMessageForm,
    CsvUploadForm,
    DrugCreateForm,
    PharmacyContactInfoForm,
    PharmacyForm,
    PharmacyReviewForm,
    PriceForm,
)
from pharmacies.models import AuditLog, ContactMessage, Pharmacy, PharmacyDrugPrice, PharmacyInvite
from pharmacies.services import contact_message_cooldown_remaining, haversine_km, log_action, upsert_price


def _parse_coords(request):
    try:
        return float(request.GET.get("lat")), float(request.GET.get("lng"))
    except (TypeError, ValueError):
        return None, None


@login_not_required
def pharmacy_list_view(request):
    """Barcha dorixonalar ro'yxati — nomi/manzili bo'yicha qidiruv, masofa
    yoki reyting bo'yicha saralash bilan."""
    query = (request.GET.get("q") or "").strip()
    sort = request.GET.get("sort") or ""
    lat, lng = _parse_coords(request)

    pharmacies = Pharmacy.objects.annotate(
        avg_rating=Avg("reviews__rating"), review_count=Count("reviews", distinct=True)
    )
    if query:
        pharmacies = pharmacies.filter(Q(name__icontains=query) | Q(address__icontains=query))
    pharmacies = list(pharmacies)

    for p in pharmacies:
        p.distance_km = round(haversine_km(lat, lng, p.lat, p.lng), 2) if lat is not None else None

    if sort == "rating":
        pharmacies.sort(key=lambda p: (p.avg_rating or 0), reverse=True)
    elif sort == "name":
        pharmacies.sort(key=lambda p: p.name.lower())
    elif lat is not None:
        pharmacies.sort(key=lambda p: p.distance_km)

    context = {
        "pharmacies": pharmacies,
        "query": query,
        "sort": sort or ("distance" if lat is not None else ""),
        "has_location": lat is not None,
        "user_lat": lat,
        "user_lng": lng,
        "map_points": [
            {
                "name": p.name, "slug": p.slug, "lat": p.lat, "lng": p.lng,
                "price": None, "distance_km": p.distance_km, "in_stock": True,
            }
            for p in pharmacies
        ],
    }
    return render(request, "pharmacies/list.html", context)


@login_not_required
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

    context = {
        "pharmacy": pharmacy,
        "prices": prices,
        "reviews": reviews,
        "review_form": review_form,
        "contact_form": ContactMessageForm(),
    }
    return render(request, "pharmacies/detail.html", context)


@login_not_required
def pharmacy_qr_view(request, slug):
    """Dorixona sahifasiga havola bo'lgan QR kodni PNG rasm sifatida
    qaytaradi — do'kon ichida chop etib qo'yish yoki mijozlarga ulashish
    uchun (masalan, staff panelidan yuklab olinadi)."""
    pharmacy = get_object_or_404(Pharmacy, slug=slug)
    url = request.build_absolute_uri(pharmacy.get_absolute_url())
    img = qrcode.make(url, box_size=8, border=2)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return HttpResponse(buf.getvalue(), content_type="image/png")


def pharmacy_contact_view(request, slug):
    pharmacy = get_object_or_404(Pharmacy, slug=slug)
    if request.method == "POST":
        cooldown = contact_message_cooldown_remaining(request.user)
        if cooldown:
            messages.error(request, f"Juda tez-tez xabar yubormoqdasiz — {cooldown} soniyadan keyin qayta urinib ko'ring.")
            return redirect("pharmacies:detail", slug=slug)
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.pharmacy = pharmacy
            msg.save()
            messages.success(request, "Xabaringiz dorixona menejeriga yuborildi.")
    return redirect("pharmacies:detail", slug=slug)


@pharmacy_staff_required
def staff_panel_view(request):
    pharmacy = request.user.pharmacy
    prices = pharmacy.prices.select_related("drug", "drug__substance").order_by("drug__trade_name")
    initial = {}
    new_drug_id = request.GET.get("new_drug")
    if new_drug_id:
        initial["drug"] = new_drug_id
    context = {
        "pharmacy": pharmacy,
        "prices": prices,
        "price_form": PriceForm(initial=initial),
        "csv_form": CsvUploadForm(),
        "contact_messages": pharmacy.contact_messages.select_related("sender")[:20],
        "contact_info_form": PharmacyContactInfoForm(instance=pharmacy),
    }
    return render(request, "pharmacies/staff_panel.html", context)


@pharmacy_staff_required
def staff_contact_info_update_view(request):
    if request.method == "POST":
        form = PharmacyContactInfoForm(request.POST, instance=request.user.pharmacy)
        if form.is_valid():
            form.save()
            log_action(request.user, f"“{request.user.pharmacy.name}” aloqa ma'lumotlarini yangiladi")
            messages.success(request, "Aloqa ma'lumotlari yangilandi.")
        else:
            messages.error(request, "Aloqa ma'lumotlarini saqlab bo'lmadi — maydonlarni tekshiring.")
    return redirect("pharmacies:staff_panel")


@pharmacy_staff_required
def resolve_contact_message_view(request, message_id):
    msg = get_object_or_404(ContactMessage, pk=message_id, pharmacy=request.user.pharmacy)
    msg.is_resolved = True
    msg.save(update_fields=["is_resolved"])
    log_action(request.user, f"“{msg.subject}” xabarini hal qilingan deb belgiladi ({msg.pharmacy.name})")

    next_url = request.POST.get("next")
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(next_url)
    return redirect("pharmacies:staff_panel")


@pharmacy_staff_required
def staff_drug_list_view(request):
    """Katalogdagi barcha dorilar — dorixona xodimi bu yerdan ko'rib,
    qidirib, kerak bo'lsa tahrirlashi mumkin (o'chirish esa yo'q — Drug
    boshqa dorixonalar bilan ham baham ko'riladi, o'chirish faqat admin
    orqali, chunki u boshqalarning narx yozuvlarini ham yo'qotib qo'yadi)."""
    query = (request.GET.get("q") or "").strip()
    drugs = Drug.objects.select_related("substance").order_by("trade_name")
    if query:
        drugs = drugs.filter(trade_name__icontains=query)
    paginator = Paginator(drugs, 50)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "pharmacies/staff_drug_list.html", {"drugs": page, "query": query})


@pharmacy_staff_required
def staff_drug_create_view(request):
    """Dorixona xodimi katalogda yo'q dorini qo'shishi uchun (masalan
    yangi yetkazib berilgan dori). Substance tanlashi shart — yangi
    substance qo'shish faqat Django admin orqali (markazlashgan nazorat)."""
    if request.method == "POST":
        form = DrugCreateForm(request.POST)
        if form.is_valid():
            drug = form.save()
            messages.success(request, f"“{drug.trade_name}” katalogga qo'shildi — endi narx belgilashingiz mumkin.")
            return redirect(f"{reverse('pharmacies:staff_panel')}?new_drug={drug.id}")
    else:
        form = DrugCreateForm()
    return render(request, "pharmacies/staff_drug_form.html", {"form": form, "is_edit": False})


@pharmacy_staff_required
def staff_drug_update_view(request, pk):
    """Mavjud dorining tafsilotlarini tuzatish (narxi emas — narx
    o'zining dorixonasi uchun alohida `staff_price_update_view` orqali)."""
    drug = get_object_or_404(Drug, pk=pk)
    if request.method == "POST":
        form = DrugCreateForm(request.POST, instance=drug)
        if form.is_valid():
            form.save()
            messages.success(request, f"“{drug.trade_name}” yangilandi.")
            return redirect("pharmacies:staff_drug_list")
    else:
        form = DrugCreateForm(instance=drug)
    return render(request, "pharmacies/staff_drug_form.html", {"form": form, "is_edit": True, "drug": drug})


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
def staff_price_delete_view(request, pk):
    price = get_object_or_404(PharmacyDrugPrice.objects.select_related("drug"), pk=pk, pharmacy=request.user.pharmacy)
    drug_name = price.drug.trade_name
    price.delete()
    log_action(request.user, f"“{drug_name}” narxini o'chirdi ({request.user.pharmacy.name})")
    messages.success(request, f"“{drug_name}” narxi o'chirildi.")
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


@pharmacy_staff_required
def staff_csv_export_view(request):
    pharmacy = request.user.pharmacy
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{pharmacy.slug}-narxlar.csv"'
    writer = csv.writer(response)
    writer.writerow(["drug_id", "trade_name", "price", "in_stock", "updated_at"])
    for row in pharmacy.prices.select_related("drug").order_by("drug__trade_name"):
        writer.writerow([row.drug_id, row.drug.trade_name, row.price, "true" if row.in_stock else "false", row.updated_at.isoformat()])
    return response


@platform_admin_required
def admin_dashboard_view(request):
    context = {
        "pharmacies": Pharmacy.objects.all().order_by("-created_at")[:50],
        "invites": PharmacyInvite.objects.select_related("pharmacy", "used_by").order_by("-created_at")[:20],
        "audit_logs": AuditLog.objects.select_related("actor")[:30],
        "stats": {
            "pharmacy_count": Pharmacy.objects.count(),
            "drug_count": Drug.objects.count(),
            "staff_count": User.objects.filter(role=UserRole.PHARMACY_STAFF).count(),
        },
        "top_drugs": Drug.objects.select_related("substance").filter(search_hits__gt=0).order_by("-search_hits")[:8],
        "active_pharmacies": Pharmacy.objects.annotate(
            price_update_count=Count("price_history")
        ).filter(price_update_count__gt=0).order_by("-price_update_count")[:8],
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
            log_action(request.user, f"“{pharmacy.name}” dorixonasini qo'shdi")
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
    log_action(request.user, f"“{pharmacy.name}” uchun taklif havolasi yaratdi")
    messages.success(request, f"Taklif havolasi yaratildi: {url}")
    return redirect("pharmacies:admin_dashboard")
