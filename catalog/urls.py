from django.urls import path

from catalog.apps import CatalogConfig
from catalog.views import catalog, contacts, contacts_success, home, our_contacts, product_detail

app_name = CatalogConfig.name

urlpatterns = [
    path("", home, name="home"),
    path("contacts/", contacts, name="contacts"),
    path("catalog/", catalog, name="catalog"),
    path("contacts_success/<str:name>/", contacts_success, name="contacts_success"),
    path("our_contacts/", our_contacts, name="our_contacts"),
    path("catalog/<int:product_id>/", product_detail, name="product_detail"),
]
