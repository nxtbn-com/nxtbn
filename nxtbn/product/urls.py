from django.conf import settings
from django.urls import path
from nxtbn.product import views as product_views


urlpatterns = [
    path("<slug:slug>/", product_views.product_details, name="product_detail"),
] 