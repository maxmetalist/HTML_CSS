from django.urls import path

from catalog.apps import CatalogConfig
from catalog.views import (
    HomeView,
    OurContactsView,
    ContactsView,
    ContactsSuccessView,
    CatalogView,
    ProductDetailView,
    ProductListView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
)

app_name = CatalogConfig.name

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("contacts/", ContactsView.as_view(), name="contacts"),
    path("catalog/", CatalogView.as_view(), name="catalog"),
    path("contacts_success/<str:name>/", ContactsSuccessView.as_view(), name="contacts_success"),
    path("our_contacts/", OurContactsView.as_view(), name="our_contacts"),
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
    path("products/", ProductListView.as_view(), name="product_list"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path("products/<int:pk>/update/", ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/delete/", ProductDeleteView.as_view(), name="product_delete"),
]
