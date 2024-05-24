from django.urls import path
from nxtbn.product.api.dashboard.views import (
    ProductListView,
    ProductDetailView,
    CategoryListView,
    CategoryDetailView,
    CollectionListView,
    CollectionDetailView
)

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<uuid:id>/', ProductDetailView.as_view(), name='product-detail'),

    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<uuid:id>/', CategoryDetailView.as_view(), name='category-detail'),

    path('collections/', CollectionListView.as_view(), name='collection-list'),
    path('collections/<uuid:id>/', CollectionDetailView.as_view(), name='collection-detail'),
]
