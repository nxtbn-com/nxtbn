from django.forms import ValidationError
from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions  import AllowAny
from rest_framework.exceptions import APIException
from rest_framework import viewsets

from rest_framework.filters import SearchFilter


from nxtbn.core.paginator import NxtbnPagination
from nxtbn.product.models import Color, Product, Category, Collection, ProductTag, ProductType, ProductVariant
from nxtbn.product.api.dashboard.serializers import (
    BasicCategorySerializer,
    ColorSerializer,
    ProductCreateSerializer,
    ProductMutationSerializer,
    ProductSerializer,
    CategorySerializer,
    CollectionSerializer,
    ProductTagSerializer,
    ProductTypeSerializer,
    ProductWithVariantSerializer,
    RecursiveCategorySerializer
)
from nxtbn.core.admin_permissions import NxtbnAdminPermission



class ProductListView(generics.ListCreateAPIView):
    permission_classes = (NxtbnAdminPermission,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = NxtbnPagination
    filter_backends = [SearchFilter]
    search_fields = ['name', 'brand']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateSerializer
        return ProductSerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (NxtbnAdminPermission,)
    queryset = Product.objects.all()
    serializer_class = ProductMutationSerializer
    lookup_field = 'id'

class ProductWithVariantView(generics.ListAPIView):
    permission_classes = (NxtbnAdminPermission,)
    queryset = Product.objects.all()
    serializer_class = ProductWithVariantSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']


class CategoryListView(generics.ListCreateAPIView):
    permission_classes = (NxtbnAdminPermission,)
    queryset = Category.objects.filter()
    serializer_class = CategorySerializer


class RecursiveCategoryListView(generics.ListCreateAPIView):
    permission_classes = (NxtbnAdminPermission,)
    queryset = Category.objects.filter(parent=None) # Get only top-level categories
    serializer_class = RecursiveCategorySerializer
    pagination_class = None

class CategoryByParentView(generics.ListAPIView):
    pagination_class = None
    permission_classes = (NxtbnAdminPermission,)
    queryset = Category.objects.all()
    serializer_class = BasicCategorySerializer
    permission_classes = (NxtbnAdminPermission,)
    
    def get_queryset(self):
        return super().get_queryset().filter(parent=self.kwargs.get('id'))

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (NxtbnAdminPermission,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (NxtbnAdminPermission,)
    lookup_field = 'id'

class CollectionViewSet(viewsets.ModelViewSet):
    pagination_class = None
    permission_classes = (NxtbnAdminPermission,)
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Collection.objects.all()
    
class ColorViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    allowed_methods = ['GET', 'POST', 'DELETE']

    def get_queryset(self):
        return Color.objects.all()
    

class ProductTypeViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer

    def get_queryset(self):
        return ProductType.objects.all()
    

class ProductTagViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = ProductTag.objects.all()
    serializer_class = ProductTagSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = response.data[:5]
        return response
    

class ProductVariantDeleteAPIView(generics.DestroyAPIView):
    queryset = ProductVariant.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Check if the variant is the default variant of any product
        if instance.product.default_variant == instance:
            raise ValidationError("This variant is set as the default variant for a product and cannot be deleted.")
        
        # If not the default variant, proceed with deletion
        return super().destroy(request, *args, **kwargs)
