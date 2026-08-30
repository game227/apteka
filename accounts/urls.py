from django.contrib.auth.views import LogoutView
from django.urls import path

from accounts import views

app_name = "accounts"

urlpatterns = [
    path("kirish/", views.AptekaLoginView.as_view(), name="login"),
    path("chiqish/", LogoutView.as_view(), name="logout"),
    path("royxat/", views.register_view, name="register"),
    path("profil/", views.profile_view, name="profile"),
]
