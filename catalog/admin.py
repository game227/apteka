from django.contrib import admin

from catalog.models import Category, Drug, DrugAlias, Favorite, SearchQuery, Substance


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name_uz", "name_ru", "icon", "order"]
    prepopulated_fields = {"slug": ("name_uz",)}


@admin.register(Substance)
class SubstanceAdmin(admin.ModelAdmin):
    list_display = ["name_inn", "name_uz", "name_ru", "category"]
    list_filter = ["category"]
    search_fields = ["name_inn", "name_uz", "name_ru"]


class DrugAliasInline(admin.TabularInline):
    model = DrugAlias
    extra = 1


@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = ["trade_name", "substance", "manufacturer", "dosage_strength", "reference_price", "search_hits"]
    list_filter = ["substance__category"]
    search_fields = ["trade_name", "manufacturer", "substance__name_inn"]
    prepopulated_fields = {"slug": ("trade_name",)}
    inlines = [DrugAliasInline]
    autocomplete_fields = ["substance"]


admin.site.site_header = "Dori narxlari — boshqaruv paneli"
admin.site.site_title = "Dori narxlari admin"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ["user", "drug", "created_at"]
    autocomplete_fields = ["drug"]


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ["query_text", "user", "result_count", "created_at"]
    readonly_fields = ["query_text", "user", "result_count", "created_at"]
