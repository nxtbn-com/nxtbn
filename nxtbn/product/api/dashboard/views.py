from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions  import AllowAny
from rest_framework.exceptions import APIException
from rest_framework import viewsets


from nxtbn.core.paginator import NxtbnPagination
from nxtbn.product.models import Color, Product, Category, Collection
from nxtbn.product.api.dashboard.serializers import (
    ColorSerializer,
    ProductCreateSerializer,
    ProductSerializer,
    CategorySerializer,
    CollectionSerializer,
    RecursiveCategorySerializer
)
from nxtbn.core.admin_permissions import NxtbnAdminPermission



class ProductListView(generics.ListCreateAPIView):
    permission_classes = (NxtbnAdminPermission,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = NxtbnPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateSerializer
        return ProductSerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (NxtbnAdminPermission,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (NxtbnAdminPermission,)
    lookup_field = 'id'


class CategoryListView(generics.ListCreateAPIView):
    permission_classes = (NxtbnAdminPermission,)
    queryset = Category.objects.filter(parent=None) # Get only top-level categories
    serializer_class = RecursiveCategorySerializer
    pagination_class = None


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (NxtbnAdminPermission,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (NxtbnAdminPermission,)
    lookup_field = 'id'


class CollectionListView(generics.ListCreateAPIView):
    permission_classes = (NxtbnAdminPermission,)
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = (NxtbnAdminPermission,)
    pagination_class = None


class CollectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (NxtbnAdminPermission,)
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = (NxtbnAdminPermission,)
    lookup_field = 'id'


class ColorViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    allowed_methods = ['GET', 'POST', 'DELETE']

    def get_queryset(self):
        return Color.objects.all()