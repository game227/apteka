from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from catalog.services import normalize_and_match
from pharmacies.services import nearby_prices
from prescriptions.models import PrescriptionScan, PrescriptionScanItem


def upload_view(request):
    return render(request, "prescriptions/upload.html")


def scan_view(request):
    if request.method != "POST" or not request.FILES.get("image"):
        return redirect("prescriptions:upload")

    scan = PrescriptionScan.objects.create(user=request.user, image=request.FILES["image"])

    from prescriptions.services import GeminiUnavailableError, scan_prescription_image

    image_bytes = scan.image.read()
    try:
        raw_names = scan_prescription_image(image_bytes, mime_type=request.FILES["image"].content_type or "image/jpeg")
    except GeminiUnavailableError:
        raw_names = []
        messages.error(
            request,
            "Retsept skaneri hozir ishlamayapti (server yoki tarmoq muammosi bo'lishi mumkin). "
            "Birozdan keyin qayta urinib ko'ring yoki dorilarni qo'lda qidiring.",
        )

    items = []
    for raw_name in raw_names:
        match = normalize_and_match(raw_name)
        item = PrescriptionScanItem.objects.create(
            scan=scan,
            raw_text=match.raw_text,
            matched_drug=match.drug,
            confidence=match.confidence,
            status=match.status,
        )
        items.append({"item": item, "candidates": match.candidates})

    return render(request, "prescriptions/review.html", {"scan": scan, "items": items})


def confirm_view(request, scan_id):
    scan = get_object_or_404(PrescriptionScan, pk=scan_id, user=request.user)
    lat = request.POST.get("lat")
    lng = request.POST.get("lng")
    lat = float(lat) if lat else None
    lng = float(lng) if lng else None

    results = []
    for item in scan.items.all():
        drug_id = request.POST.get(f"drug_{item.id}")
        if not drug_id:
            continue
        item.confirmed_drug_id = int(drug_id)
        item.save(update_fields=["confirmed_drug"])
        prices = nearby_prices(item.confirmed_drug_id, lat, lng, radius_km=15)
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
        results.append(
            {
                "drug": item.confirmed_drug,
                "prices": prices,
                "map_points": map_points,
                "map_id": f"pharmacy-map-{item.id}",
                "data_id": f"map-data-{item.id}",
            }
        )

    return render(request, "prescriptions/result.html", {"scan": scan, "results": results, "user_lat": lat, "user_lng": lng})


def history_view(request):
    scans = PrescriptionScan.objects.filter(user=request.user).prefetch_related("items")
    return render(request, "prescriptions/history.html", {"scans": scans})
