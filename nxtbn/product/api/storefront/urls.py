from django.urls import path
from nxtbn.product.api.storefront import views as product_views

urlpatterns = [
    path('products/', product_views.ProductListView.as_view(), name='product-list'),
    path('products/<slug:slug>/', product_views.ProductDetailView.as_view(), name='product-detail'),
    path('collections/', product_views.CollectionListView.as_view(), name='collection-list'),
    path('categories/', product_views.CategoryListView.as_view(), name='category-list'),
]
