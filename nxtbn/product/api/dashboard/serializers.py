from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.db import transaction

from nxtbn.product.models import Product, Category, Collection, ProductVariant

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'parent', 'subcategories',)
        ref_name = 'category_dashboard_get'


class RecursiveCategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'subcategories')

    def get_subcategories(self, obj):
        subcategories = obj.subcategories.all()
        return RecursiveCategorySerializer(subcategories, many=True).data

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ('id', 'name', 'description', 'is_active', 'image',)
        ref_name = 'collection_dashboard_get'

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        ref_name = 'product_variant_dashboard_get'
        fields = ('id', 'product', 'name', 'compare_at_price', 'price', 'cost_per_unit', 'sku',)

class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product 
        ref_name = 'product_dashboard_get'
        fields =  (
            'id',
            'name',
            'summary',
            'description',
            'media',
            'category',
            'vendor',
            'brand',
            'type',
            'related_to',
            'default_variant',
            'collections',
            'variants',
        )
