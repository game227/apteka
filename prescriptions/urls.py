from django.urls import path

from prescriptions import views

app_name = "prescriptions"

urlpatterns = [
    path("", views.upload_view, name="upload"),
    path("skanerlash/", views.scan_view, name="scan"),
    path("<int:scan_id>/tasdiqlash/", views.confirm_view, name="confirm"),
    path("tarix/", views.history_view, name="history"),
]
