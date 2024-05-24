from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.db import transaction

from nxtbn.product.models import Product, Category, Collection, ProductVariant

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'parent', 'subcategories',)


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

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ('id', 'product', 'name', 'compare_at_price', 'price', 'cost_per_unit', 'sku',)

class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product 
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
            'currency',
            'default_variant',
            'collections',
            'variants',
        )
