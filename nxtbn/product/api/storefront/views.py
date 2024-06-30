from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions  import AllowAny
from rest_framework.exceptions import APIException

from rest_framework import filters as drf_filters
import django_filters
from django_filters import rest_framework as filters


from nxtbn.core.paginator import NxtbnPagination
from nxtbn.product.api.storefront.serializers import CategorySerializer, CollectionSerializer, ProductDetailSerializer, ProductSerializer
from nxtbn.product.models import Category, Collection, Product
from nxtbn.product.models import Supplier


class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    summary = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    category = filters.ModelChoiceFilter(field_name='category', queryset=Category.objects.all())
    supplier = filters.ModelChoiceFilter(field_name='supplier', queryset=Supplier.objects.all())
    brand = filters.CharFilter(lookup_expr='icontains')
    type = filters.CharFilter(field_name='type', lookup_expr='exact')
    related_to = filters.CharFilter(field_name='related_to__name', lookup_expr='icontains')
    collection = filters.ModelChoiceFilter(field_name='collections', queryset=Collection.objects.all())

    class Meta:
        model = Product
        fields = ('name', 'summary', 'description', 'category', 'supplier', 'brand', 'type', 'related_to', 'collection')


    


class ProductListView(generics.ListAPIView):
    pagination_class = NxtbnPagination
    permission_classes = (AllowAny,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        drf_filters.SearchFilter,
        drf_filters.OrderingFilter
    ]
    filterset_class = ProductFilter
    search_fields = ['name', 'summary', 'description', 'category__name', 'type']
    ordering_fields = ['name', 'created_at']

class CollectionListView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    pagination_class = None
    queryset = Collection.objects.filter(is_active=True)
    serializer_class = CollectionSerializer

class CategoryListView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    pagination_class = None
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductDetailView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'