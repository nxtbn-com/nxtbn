from django.urls import path
from nxtbn.invoice.api.dashboard.views import InvoiceListCreateView, InvoiceDetailView

urlpatterns = [
    path('invoices/', InvoiceListCreateView.as_view(), name='invoice-list'),
    path('invoices/<int:id>/', InvoiceDetailView.as_view(), name='invoice-detail')
]
