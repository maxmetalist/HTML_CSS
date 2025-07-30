from django.urls import path

from catalog.apps import CatalogConfig
from catalog.views import catalog, contacts, contacts_success, home

app_name = CatalogConfig.name

urlpatterns = [
    path("", home, name="home"),
    path("contacts/", contacts, name="contacts"),
    path("catalog/", catalog, name="catalog"),
    path("contacts_success/<str:name>/", contacts_success, name="contacts_success"),
    path("our_contacts/", contacts, name="our_contacts"),
]
