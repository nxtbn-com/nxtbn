from django.shortcuts import render
from django.urls import path, include
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


API_INFO = openapi.Info(
    title="nxtbn API",
    default_version="v1",
    description="API documentation for nxtbn App",
)

DASHBOARD_API_DOCS_SCHEMA_VIEWS = get_schema_view(
    API_INFO,
    public=True,
    permission_classes=(AllowAny,),
    patterns=[
        path('user/dashboard/api/', include('nxtbn.users.api.dashboard.urls')),
        path('core/dashboard/api/', include('nxtbn.core.api.dashboard.urls')),
        path('invoice/dashboard/api/', include('nxtbn.invoice.api.dashboard.urls')),
        path('vendor/dashboard/api/', include('nxtbn.vendor.api.dashboard.urls')),
        path('filemanager/dashboard/api/', include('nxtbn.filemanager.api.dashboard.urls')),
        path('order/dashboard/api/', include('nxtbn.order.api.dashboard.urls')),
        path('product/dashboard/api/', include('nxtbn.product.api.dashboard.urls')),
        path('payment/dashboard/api/', include('nxtbn.payment.api.dashboard.urls')),
        path('seo/dashboard/api/', include('nxtbn.seo.api.dashboard.urls')),
    ]
)


STOREFRONT_API_DOCS_SCHEMA_VIEWS = get_schema_view(
    API_INFO,
    public=True,
    permission_classes=(AllowAny,),
    patterns=[
        path('user/storefront/api/', include('nxtbn.users.api.storefront.urls')),
        path('core/storefront/api/', include('nxtbn.core.api.storefront.urls')),
        path('invoice/storefront/api/', include('nxtbn.invoice.api.storefront.urls')),
        path('vendor/storefront/api/', include('nxtbn.vendor.api.storefront.urls')),
        path('filemanager/storefront/api/', include('nxtbn.filemanager.api.storefront.urls')),
        path('order/storefront/api/', include('nxtbn.order.api.storefront.urls')),
        path('product/storefront/api/', include('nxtbn.product.api.storefront.urls')),
        path('payment/storefront/api/', include('nxtbn.payment.api.storefront.urls')),
        path('seo/storefront/api/', include('nxtbn.seo.api.storefront.urls')),
    ]
)


def api_docs(request):
    return render(request, "api_docs.html") 