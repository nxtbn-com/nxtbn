from django.urls import path

from nxtbn.cart.api.storefront import views as cart_views

urlpatterns = [
    path('carts/', cart_views.CartItemListView.as_view(), name='cart-list'),
]