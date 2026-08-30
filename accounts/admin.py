from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from accounts.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """`role` — bu ilovada foydalanuvchi nima qila olishini belgilaydigan
    YAGONA maydon. Django'ning o'z ruxsat tizimi (is_superuser, groups,
    user_permissions) ataylab formadan yashirilgan: ular `role`dan
    mustaqil ishlaydi va ularni shu yerda o'zgartirish "role'ni
    o'zgartirdim-u hech narsa bo'lmadi" chalkashligiga olib keladi.
    Admin (superuser) huquqi faqat serverdan `createsuperuser` bilan
    beriladi — bu qiymatlar shu yerda ko'rsatilmasa ham o'zgarmasdan
    saqlanib qoladi."""

    list_display = ["username", "first_name", "last_name", "role", "pharmacy", "is_active"]
    list_filter = ["role", "is_active"]
    search_fields = ["username", "first_name", "last_name", "email", "phone"]
    readonly_fields = ["last_login", "date_joined"]
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Shaxsiy ma'lumot", {"fields": ("first_name", "last_name", "email", "phone")}),
        ("Platforma huquqi", {
            "fields": ("role", "pharmacy", "is_active"),
            "description": (
                "\"pharmacy_staff\" tanlansa, dorixona ham tanlanishi shart — "
                "shundagina o'sha xodim shu dorixona narxlarini boshqara oladi. "
                "\"Admin\" bu yerda yo'q — u faqat serverdan (createsuperuser) beriladi."
            ),
        }),
        ("Sanalar", {"fields": ("last_login", "date_joined"), "classes": ("collapse",)}),
    )
