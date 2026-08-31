from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.views import LogoutView
from django.urls import path, reverse_lazy

from accounts import views
from accounts.forms import StyledPasswordResetForm, StyledSetPasswordForm

app_name = "accounts"

urlpatterns = [
    path("kirish/", views.AptekaLoginView.as_view(), name="login"),
    path("chiqish/", LogoutView.as_view(), name="logout"),
    path("royxat/", views.register_view, name="register"),
    path("profil/", views.profile_view, name="profile"),
    path("xabarlar/", views.notifications_view, name="notifications"),
    path(
        "parol-tiklash/",
        login_not_required(
            auth_views.PasswordResetView.as_view(
                template_name="accounts/password_reset.html",
                email_template_name="accounts/password_reset_email.html",
                subject_template_name="accounts/password_reset_subject.txt",
                success_url=reverse_lazy("accounts:password_reset_done"),
                form_class=StyledPasswordResetForm,
            )
        ),
        name="password_reset",
    ),
    path(
        "parol-tiklash/yuborildi/",
        login_not_required(auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html")),
        name="password_reset_done",
    ),
    path(
        "parol-tiklash/<uidb64>/<token>/",
        login_not_required(
            auth_views.PasswordResetConfirmView.as_view(
                template_name="accounts/password_reset_confirm.html",
                success_url=reverse_lazy("accounts:password_reset_complete"),
                form_class=StyledSetPasswordForm,
            )
        ),
        name="password_reset_confirm",
    ),
    path(
        "parol-tiklash/tugadi/",
        login_not_required(
            auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html")
        ),
        name="password_reset_complete",
    ),
]
