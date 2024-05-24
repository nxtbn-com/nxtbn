from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.db import transaction

from nxtbn.product.api.dashboard.serializers import RecursiveCategorySerializer
from nxtbn.filemanager.api.dashboard.serializers import ImageSerializer
from nxtbn.product.models import Product, Collection, Category, ProductVariant

class CategorySerializer(RecursiveCategorySerializer):
    pass

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ('id', 'name', 'description', 'is_active', 'image',)


class ProductVariantSerializer(serializers.ModelSerializer):
    variant_image = ImageSerializer(many=True, read_only=True)
    class Meta:
        model = ProductVariant
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    default_variant = ProductVariantSerializer()
    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'summary',
            'description',
            'category',
            'brand',
            'type',
            'currency',
            'slug',
            'default_variant',
        )


class ProductDetailSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True)
    default_variant = ProductVariantSerializer()
    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'summary',
            'description',
            'brand',
            'type',
            'currency',
            'category',
            'collections',
            'media',
            'created_by',
            'default_variant',
            'variants',
        )