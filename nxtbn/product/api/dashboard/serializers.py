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
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'children')

    def get_children(self, obj):
        children = obj.subcategories.all()
        return RecursiveCategorySerializer(children, many=True).data

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


class ProductCreateSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        ref_name = 'product_dashboard_create'
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
            'variants',
            'collections',
        )

    def create(self, validated_data):
        collection = validated_data.pop('collections', [])
        isinstance = Product.objects.create(
            **validated_data,
            **{'created_by': self.context['request'].user}
        )

        isinstance.collections.set(collection)
        return isinstance