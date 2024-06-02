from django.urls import path
from nxtbn.payment.api.storefront import views as payment_views

urlpatterns = [
    path('start-payment/<str:payment_plugin_id>/', payment_views.StartPaymentProcess.as_view(), name='start-payment'),
    path('non-sensitive-payment-info/<str:payment_plugin_id>/', payment_views.NonSensitivePaymentKey.as_view(), name='non_sensitive_payment_info'),
    path('webhook-view/<str:payment_plugin_id>/', payment_views.WebhookAPIView.as_view(), name='webhook_view'),
]
