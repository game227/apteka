from django.urls import path

from catalog import views

app_name = "catalog"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("qidiruv/taklif/", views.search_suggest_view, name="search_suggest"),
    path("turkumlar/", views.category_list_view, name="category_list"),
    path("turkum/<slug:slug>/", views.category_detail_view, name="category"),
    path("dori/<slug:slug>/", views.drug_detail_view, name="drug_detail"),
    path("dori/<int:drug_id>/sevimli/", views.toggle_favorite_view, name="toggle_favorite"),
    path("haqida/", views.about_view, name="about"),
]
