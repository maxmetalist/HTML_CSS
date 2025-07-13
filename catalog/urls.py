from django.urls import path
from catalog.apps import CatalogConfig
from catalog.views import home, contacts, catalog, contacts_success

app_name = CatalogConfig.name

urlpatterns = [
    path("", home, name="home"),
    path("contacts/", contacts, name="contacts"),
    path("catalog/", catalog, name="catalog"),
    path('contacts_success/<str:name>/', contacts_success, name='contacts_success'),
]
