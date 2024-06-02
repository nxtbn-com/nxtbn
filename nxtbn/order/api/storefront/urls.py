from django.urls import path
from nxtbn.order.api.storefront import views as order_views

urlpatterns = [
    path('orders/', order_views.OrderListView.as_view(), name='order-list'),

    # place order
    path('guest-user-order-create/', order_views.GuestUserOrderCreateAPIView.as_view(), name='guest-user-order-create'),
    path('user-order-create/', order_views.OrderCreateAPIView.as_view(), name='user-order-create'),
]
