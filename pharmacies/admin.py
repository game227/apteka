from django.contrib import admin

from pharmacies.models import AuditLog, ContactMessage, Pharmacy, PharmacyDrugPrice, PharmacyInvite, PharmacyReview, PriceHistory


class PharmacyDrugPriceInline(admin.TabularInline):
    model = PharmacyDrugPrice
    extra = 0
    autocomplete_fields = ["drug"]
    fields = ["drug", "price", "in_stock", "updated_at"]
    readonly_fields = ["updated_at"]


@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ["name", "address", "phone", "lat", "lng", "created_at"]
    search_fields = ["name", "address"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [PharmacyDrugPriceInline]


@admin.register(PharmacyInvite)
class PharmacyInviteAdmin(admin.ModelAdmin):
    list_display = ["pharmacy", "token", "used_by", "expires_at", "is_valid"]
    readonly_fields = ["token"]
    autocomplete_fields = ["pharmacy"]


@admin.register(PharmacyReview)
class PharmacyReviewAdmin(admin.ModelAdmin):
    list_display = ["pharmacy", "user", "rating", "created_at"]
    list_filter = ["rating"]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["pharmacy", "sender", "subject", "is_resolved", "created_at"]
    list_filter = ["is_resolved", "pharmacy"]
    readonly_fields = ["sender", "pharmacy", "subject", "message", "created_at"]


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ["pharmacy", "drug", "price", "in_stock", "recorded_at"]
    list_filter = ["pharmacy"]
    readonly_fields = ["pharmacy", "drug", "price", "in_stock", "changed_by", "recorded_at"]

    def has_add_permission(self, request):
        return False


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["actor", "action", "created_at"]
    list_filter = ["actor"]
    readonly_fields = ["actor", "action", "created_at"]

    def has_add_permission(self, request):
        return False
