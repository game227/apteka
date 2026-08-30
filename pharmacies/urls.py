from django.urls import path

from pharmacies import views

app_name = "pharmacies"

urlpatterns = [
    path("panel/", views.staff_panel_view, name="staff_panel"),
    path("panel/narx/", views.staff_price_update_view, name="staff_price_update"),
    path("panel/csv/", views.staff_csv_upload_view, name="staff_csv_upload"),
    path("admin-panel/", views.admin_dashboard_view, name="admin_dashboard"),
    path("admin-panel/yangi/", views.admin_pharmacy_create_view, name="admin_pharmacy_create"),
    path("admin-panel/<int:pharmacy_id>/taklif/", views.admin_invite_create_view, name="admin_invite_create"),
    path("<slug:slug>/", views.pharmacy_detail_view, name="detail"),
]
