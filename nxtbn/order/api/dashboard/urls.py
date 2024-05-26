from django.urls import path

from nxtbn.order.api.dashboard import views as order_views


urlpatterns = [
    path('orders/', order_views.OrderListView.as_view(), name='order-list'),
    path('orders/<uuid:id>/', order_views.OrderDetailView.as_view(), name='order-detail'),
    path('stats/', order_views.OrderStatsView.as_view(), name='order-stats'),
]
