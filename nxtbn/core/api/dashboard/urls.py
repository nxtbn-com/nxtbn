from django.urls import path
from nxtbn.core.api.dashboard import views as core_views

urlpatterns = [
    path('upload-pluggins/', core_views.PlugginsUploadView.as_view(), name='upload_pluggins'),
    path('upload-payment-plugins/', core_views.UploadPaymentPlugin.as_view(), name='upload_payment_plugins'),
    path('upload-payment-pluggin-install/', core_views.UploadInstallPaymentPlugins.as_view(), name='upload_payment_pluggin_install'),
]
