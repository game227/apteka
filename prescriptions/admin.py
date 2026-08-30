from django.contrib import admin

from prescriptions.models import PrescriptionScan, PrescriptionScanItem


class PrescriptionScanItemInline(admin.TabularInline):
    model = PrescriptionScanItem
    extra = 0
    readonly_fields = ["raw_text", "matched_drug", "confirmed_drug", "confidence", "status"]


@admin.register(PrescriptionScan)
class PrescriptionScanAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "created_at"]
    inlines = [PrescriptionScanItemInline]
