from django.contrib import messages
from django.contrib.auth.decorators import login_not_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalog.models import Category, Drug, Favorite, SearchQuery, Substance
from catalog.services import normalize_and_match
from pharmacies.forms import ContactMessageForm
from pharmacies.services import contact_message_cooldown_remaining, nearby_pharmacies, nearby_prices


def _parse_coords(request):
    try:
        return float(request.GET.get("lat")), float(request.GET.get("lng"))
    except (TypeError, ValueError):
        return None, None


@login_not_required
def home_view(request):
    query = (request.GET.get("q") or "").strip()
    results = []
    if query:
        results = list(
            Drug.objects.select_related("substance")
            .filter(Q(trade_name__icontains=query) | Q(aliases__alias_text__icontains=query))
            .distinct()[:30]
        )
        if not results:
            match = normalize_and_match(query, use_gemini_fallback=False)
            results = [c.drug_id for c in match.candidates]
            results = list(Drug.objects.select_related("substance").filter(id__in=results))
        SearchQuery.objects.create(
            user=request.user if request.user.is_authenticated else None,
            query_text=query,
            result_count=len(results),
        )

    lat, lng = _parse_coords(request)
    pharmacies = nearby_pharmacies(lat, lng)[:12]
    map_points = [
        {"name": p.name, "slug": p.slug, "lat": p.lat, "lng": p.lng, "price": None, "distance_km": p.distance_km, "in_stock": True}
        for p in pharmacies
    ]

    context = {
        "query": query,
        "results": results,
        "categories": Category.objects.all()[:8],
        "popular_drugs": Drug.objects.select_related("substance").order_by("-search_hits")[:8],
        "has_location": lat is not None,
        "map_points": map_points,
        "user_lat": lat,
        "user_lng": lng,
    }
    return render(request, "catalog/home.html", context)


@login_not_required
def search_suggest_view(request):
    query = (request.GET.get("q") or "").strip()
    if len(query) < 2:
        return JsonResponse({"results": []})
    drugs = Drug.objects.filter(trade_name__icontains=query).select_related("substance")[:8]
    return JsonResponse(
        {
            "results": [
                {"id": d.id, "trade_name": d.trade_name, "substance": d.substance.name_inn, "url": d.get_absolute_url()}
                for d in drugs
            ]
        }
    )


@login_not_required
def category_list_view(request):
    categories = Category.objects.prefetch_related("substances")
    return render(request, "catalog/category_list.html", {"categories": categories})


@login_not_required
def category_detail_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    drugs = Drug.objects.select_related("substance").filter(substance__category=category)
    paginator = Paginator(drugs, 24)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "catalog/category_detail.html", {"category": category, "drugs": page})


@login_not_required
def drug_detail_view(request, slug):
    drug = get_object_or_404(Drug.objects.select_related("substance"), slug=slug)
    Drug.objects.filter(pk=drug.pk).update(search_hits=drug.search_hits + 1)

    lat, lng = _parse_coords(request)
    radius_km = float(request.GET.get("radius_km", 15))
    prices = nearby_prices(drug.id, lat, lng, radius_km)

    alternatives = (
        Drug.objects.select_related("substance")
        .filter(substance=drug.substance)
        .exclude(pk=drug.pk)
    )

    price_trend = list(drug.price_history.order_by("recorded_at").values("price", "recorded_at")[:60])

    is_favorite = (
        request.user.is_authenticated and Favorite.objects.filter(user=request.user, drug=drug).exists()
    )

    map_points = [
        {
            "name": row.pharmacy.name,
            "slug": row.pharmacy.slug,
            "lat": row.pharmacy.lat,
            "lng": row.pharmacy.lng,
            "price": float(row.price),
            "distance_km": row.distance_km,
            "in_stock": row.in_stock,
        }
        for row in prices
    ]

    context = {
        "drug": drug,
        "prices": prices,
        "alternatives": alternatives,
        "is_favorite": is_favorite,
        "has_location": lat is not None,
        "price_trend": price_trend,
        "map_points": map_points,
        "user_lat": lat,
        "user_lng": lng,
    }
    return render(request, "catalog/drug_detail.html", context)


@require_POST
def toggle_favorite_view(request, drug_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login_required"}, status=401)
    drug = get_object_or_404(Drug, pk=drug_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, drug=drug)
    if not created:
        fav.delete()
    return redirect(request.META.get("HTTP_REFERER") or drug.get_absolute_url())


@login_not_required
def about_view(request):
    return render(request, "catalog/about.html")


@login_not_required
def terms_view(request):
    return render(request, "catalog/terms.html")


def contact_view(request):
    if request.method == "POST":
        cooldown = contact_message_cooldown_remaining(request.user)
        if cooldown:
            messages.error(request, f"Juda tez-tez xabar yubormoqdasiz — {cooldown} soniyadan keyin qayta urinib ko'ring.")
            return redirect("catalog:contact")
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.save()
            messages.success(request, "Xabaringiz yuborildi — admin/moderator tez orada bog'lanadi.")
            return redirect("catalog:contact")
    else:
        form = ContactMessageForm()
    return render(request, "catalog/contact.html", {"form": form})
