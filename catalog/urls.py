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
    ProductDeleteView, ProductUnpublishView, ProductModerationListView, ProductModerationDashboard, ProductPublishView,
    ProductChangeStatusView, MassUnpublishView,
)

app_name = CatalogConfig.name

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("contacts/", ContactsView.as_view(), name="contacts"),
    path("catalog/", CatalogView.as_view(), name="catalog"),
    path("contacts_success/<str:name>/", ContactsSuccessView.as_view(), name="contacts_success"),
    path("our_contacts/", OurContactsView.as_view(), name="our_contacts"),
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
    path("product/", ProductListView.as_view(), name="product_list"),
    path("product/create/", ProductCreateView.as_view(), name="product_create"),
    path("product/<int:pk>/update/", ProductUpdateView.as_view(), name="product_update"),
    path("product/<int:pk>/delete/", ProductDeleteView.as_view(), name="product_delete"),
    path('product/<int:pk>/publish/', ProductPublishView.as_view(), name='product_publish'),
    path('product/<int:pk>/unpublish/', ProductUnpublishView.as_view(), name='product_unpublish'),
    path('mass-unpublish/', MassUnpublishView.as_view(), name='mass_unpublish'),
    path('product/<int:pk>/change-status/', ProductChangeStatusView.as_view(), name='product_change_status'),
    path('moderation/', ProductModerationListView.as_view(), name='product_moderation'),
    path('moderation/dashboard/', ProductModerationDashboard.as_view(), name='moderation_dashboard'),
]
