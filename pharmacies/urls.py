from django.urls import path

from pharmacies import views

app_name = "pharmacies"

urlpatterns = [
    path("", views.pharmacy_list_view, name="list"),
    path("panel/", views.staff_panel_view, name="staff_panel"),
    path("panel/dorilar/", views.staff_drug_list_view, name="staff_drug_list"),
    path("panel/dori-qoshish/", views.staff_drug_create_view, name="staff_drug_create"),
    path("panel/dorilar/<int:pk>/tahrirlash/", views.staff_drug_update_view, name="staff_drug_update"),
    path("panel/narx/", views.staff_price_update_view, name="staff_price_update"),
    path("panel/narx/<int:pk>/ochirish/", views.staff_price_delete_view, name="staff_price_delete"),
    path("panel/csv/", views.staff_csv_upload_view, name="staff_csv_upload"),
    path("panel/csv/eksport/", views.staff_csv_export_view, name="staff_csv_export"),
    path("panel/aloqa/", views.staff_contact_info_update_view, name="staff_contact_info_update"),
    path("admin-panel/", views.admin_dashboard_view, name="admin_dashboard"),
    path("admin-panel/yangi/", views.admin_pharmacy_create_view, name="admin_pharmacy_create"),
    path("admin-panel/<int:pharmacy_id>/taklif/", views.admin_invite_create_view, name="admin_invite_create"),
    path("panel/xabar/<int:message_id>/hal-qildim/", views.resolve_contact_message_view, name="resolve_contact_message"),
    path("<slug:slug>/boglanish/", views.pharmacy_contact_view, name="contact"),
    path("<slug:slug>/qr/", views.pharmacy_qr_view, name="qr"),
    path("<slug:slug>/", views.pharmacy_detail_view, name="detail"),
]
