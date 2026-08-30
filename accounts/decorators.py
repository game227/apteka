from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def pharmacy_staff_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_pharmacy_staff and request.user.pharmacy_id):
            messages.error(request, "Bu sahifa faqat dorixona xodimlari uchun.")
            return redirect("catalog:home")
        return view_func(request, *args, **kwargs)

    return wrapper


def platform_admin_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_platform_admin:
            messages.error(request, "Bu sahifa faqat administratorlar uchun.")
            return redirect("catalog:home")
        return view_func(request, *args, **kwargs)

    return wrapper
