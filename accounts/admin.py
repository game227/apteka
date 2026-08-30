from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from accounts.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ["username", "first_name", "last_name", "role", "pharmacy", "is_active"]
    list_filter = ["role", "is_active", "is_staff"]
    search_fields = ["username", "first_name", "last_name", "email", "phone"]
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Platforma", {"fields": ("role", "phone", "pharmacy")}),
    )
