from django.urls import path

from catalog.apps import CatalogConfig
from catalog.views import HomeView, OurContactsView, ContactsView, ContactsSuccessView, CatalogView, ProductDetailView

app_name = CatalogConfig.name

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("contacts/", ContactsView.as_view(), name="contacts"),
    path("catalog/", CatalogView.as_view(), name="catalog"),
    path("contacts_success/<str:name>/", ContactsSuccessView.as_view(), name="contacts_success"),
    path("our_contacts/", OurContactsView.as_view(), name="our_contacts"),
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
]
