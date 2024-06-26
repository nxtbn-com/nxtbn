from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.db import transaction

from nxtbn.core.models import CurrencyExchange
from nxtbn.product.api.dashboard.serializers import RecursiveCategorySerializer
from nxtbn.filemanager.api.dashboard.serializers import ImageSerializer
from nxtbn.product.models import Product, Collection, Category, ProductVariant

from nxtbn.core.currency.backend import currency_Backend

class CategorySerializer(RecursiveCategorySerializer):
    pass

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ('id', 'name', 'description', 'is_active', 'image',)


class ProductVariantSerializer(serializers.ModelSerializer):
    variant_image = ImageSerializer(many=True, read_only=True)
    price_in_target_currency = serializers.SerializerMethodField()
    class Meta:
        model = ProductVariant
        fields = '__all__'

    def get_price_in_target_currency(self, obj):
        if not settings.IS_MULTI_CURRENCY:
            return obj.price
        else:
            currency_code = self.context.get('request').currency
            price = currency_Backend().to_target_currency(currency_code, obj.price)
        return price

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
            'category',
            'collections',
            'images',
            'created_by',
            'default_variant',
            'variants',
        )