from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.db import transaction
from rest_framework.exceptions import ValidationError


from nxtbn.core import PublishableStatus
from nxtbn.filemanager.api.dashboard.serializers import ImageSerializer
from nxtbn.product.models import Color, Product, Category, Collection, ProductTag, ProductType, ProductVariant

class ProductTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTag
        fields = '__all__'

        

class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = '__all__'

    def create(self, validated_data):
        # Check if the product is a physical product
        if validated_data.get('physical_product') and not validated_data.get('weight_unit'):
            raise ValidationError({'weight_unit': 'This field is required for physical products.'})

        # Create the ProductType instance
        return super().create(validated_data)
    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'parent', 'subcategories',)
        read_only_fields = ('subcategories',)
        ref_name = 'category_dashboard_get'

class NameIDCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name',)

class BasicCategorySerializer(serializers.ModelSerializer):
    parent = NameIDCategorySerializer(read_only=True)
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'parent', 'has_sub')
        read_only_fields = ('subcategories',)
        ref_name = 'category_dashboard_basic'

class RecursiveCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'children')

    def get_children(self, obj):
        children = obj.subcategories.all()
        return RecursiveCategorySerializer(children, many=True).data

class CollectionSerializer(serializers.ModelSerializer):
    images_details = ImageSerializer(read_only=True, source='image')
    class Meta:
        model = Collection
        fields = (
            'id',
            'name',
            'description',
            'is_active',
            'image',
            'images_details',
        )
        ref_name = 'collection_dashboard_get'
        write_only_fields = ('image',)

class ProductVariantSerializer(serializers.ModelSerializer):
    is_default_variant = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    class Meta:
        model = ProductVariant
        ref_name = 'product_variant_dashboard_get'
        fields = (
            'id',
            'product',
            'product_name',
            'name',
            'compare_at_price',
            'price',
            'cost_per_unit',
            'sku',
            'weight_unit',
            'weight_value',
            'stock',
            'color_code',
            'track_inventory',
            'stock_status',
            'low_stock_threshold',
            'variant_image',
            'is_default_variant',
        )
    def get_is_default_variant(self, obj):
        return obj.product.default_variant_id == obj.id
    
    def get_product_name(self, obj):
        return obj.product.name  

class ProductSerializer(serializers.ModelSerializer):
    default_variant = ProductVariantSerializer(read_only=True)
    product_thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Product 
        ref_name = 'product_dashboard_get'
        fields =  (
            'id',
            'name',
            'summary',
            'description',
            'images',
            'category',
            'supplier',
            'brand',
            'product_type',
            'related_to',
            'default_variant',
            'collections',
            'product_thumbnail',
            'colors',
        )
    
    def get_product_thumbnail(self, obj):
        return obj.product_thumbnail(self.context['request'])

class VariantCreatePayloadSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=255, required=False)
    compare_at_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=3)
    cost_per_unit = serializers.DecimalField(max_digits=10, decimal_places=3)
    sku = serializers.CharField(max_length=255, required=False)
    stock = serializers.IntegerField(required=False)
    weight_unit = serializers.CharField(max_length=10, required=False, allow_null=True)
    weight_value = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    color_code = serializers.CharField(max_length=7, required=False, allow_null=True)
    is_default_variant = serializers.BooleanField(default=False)


class ProductDetailsSerializer(serializers.ModelSerializer):
    default_variant = ProductVariantSerializer(read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    images_details = ImageSerializer(many=True, read_only=True, source='images')
    category_details = CategorySerializer(read_only=True, source='category')
    product_type_details = ProductTypeSerializer(read_only=True, source='product_type')
    variants_payload = VariantCreatePayloadSerializer(many=True, write_only=True)
    variant_to_delete = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    tags = ProductTagSerializer(many=True, read_only=True)
    tags_payload = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField(max_length=255)),
        write_only=True,
        required=False
    )

    class Meta:
        model = Product 
        ref_name = 'product_dashboard_get'
        fields =  (
            'id',
            'slug',
            'name',
            'summary',
            'description',
            'images',
            'images_details',
            'category',
            'supplier',
            'brand',
            'product_type',
            'related_to',
            'default_variant',
            'collections',
            'colors',
            'meta_title',
            'meta_description',
            'category_details',
            'product_type_details',
            'variants',
            'variants_payload',
            'variant_to_delete',
            'tags',
            'tags_payload',
            'status',
            'is_live',
        )
    
    def update(self, instance, validated_data):
        collection = validated_data.pop('collections', [])
        images = validated_data.pop('images', [])
        variants_payload = validated_data.pop('variants_payload', [])
        currency = validated_data.pop('currency', 'USD')
        category = validated_data.pop('category', None)
        product_type = validated_data.pop('product_type', None)
        related_to = validated_data.pop('related_to', None)
        supplier = validated_data.pop('supplier', None)
        variant_to_delete = validated_data.pop('variant_to_delete', [])
        tags_payload = validated_data.pop('tags_payload', [])

        with transaction.atomic():
            instance.collections.set(collection)
            instance.images.set(images)
            if category:
                instance.category = category
            if product_type:
                instance.product_type = product_type
            if related_to:
                instance.related_to = related_to
            if supplier:    
                instance.supplier = supplier

            for pattr, pvalue in validated_data.items():
                setattr(instance, pattr, pvalue)


        
            # Delete variants
            for variant_id in variant_to_delete:
                variant = ProductVariant.objects.get(id=variant_id)
                if instance.default_variant == variant:
                    raise serializers.ValidationError({'variant_to_delete': _('The default variant cannot be deleted.')})
                variant.delete()

            default_variant = None

            for variant_data in variants_payload:
                is_default_variant = variant_data.pop('is_default_variant', False)
                variant_id = variant_data.pop('id', None)
                if variant_id:
                    # Update existing variant
                    variant = ProductVariant.objects.get(id=variant_id, product=instance)
                    for attr, value in variant_data.items():
                        setattr(variant, attr, value)
                    variant.save()
                else:
                    # Create new variant
                    ProductVariant.objects.create(product=instance, **variant_data)

                if is_default_variant:
                    default_variant = variant

            # Ensure a default variant is set
            if default_variant:
                instance.default_variant = default_variant
            elif not instance.default_variant:
                raise serializers.ValidationError({'default_variant': _('A default variant must be set.')})
            
            if tags_payload:
                instance.tags.clear()
                for tag_payload in tags_payload:
                    tag, _ = ProductTag.objects.get_or_create(name=tag_payload['value'])
                    instance.tags.add(tag)

            if instance.status == PublishableStatus.PUBLISHED:
                instance.is_live = True
            else:
                instance.is_live = False

        instance.save()
        return instance
    



class ProductCreateSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    variants_payload = VariantCreatePayloadSerializer(many=True, write_only=True)
    currency = serializers.CharField(max_length=3, required=False, write_only=True)
    tags = ProductTagSerializer(many=True, read_only=True)
    tags_payload = serializers.ListField(child=serializers.CharField(max_length=255), write_only=True, required=False)
    class Meta:
        model = Product
        ref_name = 'product_dashboard_create'
        fields =  (
            'id',
            'slug',
            'name',
            'summary',
            'description',
            'images',
            'category',
            'supplier',
            'brand',
            'product_type',
            'related_to',
            'default_variant',
            'variants',
            'collections',

            # write only fields
            'variants_payload',
            'currency',
            'meta_title',
            'meta_description',
            'tags',
            'tags_payload',
            'status',
            'is_live',
        )


    def create(self, validated_data):
        collection = validated_data.pop('collections', [])
        images = validated_data.pop('images', [])
        variants_payload = validated_data.pop('variants_payload', [])
        tags_payload = validated_data.pop('tags_payload', [])
        currency = validated_data.pop('currency', 'USD')

        with transaction.atomic():
            instance = Product.objects.create(
                **validated_data,
                **{'created_by': self.context['request'].user}
            )

            instance.collections.set(collection)
            instance.images.set(images)

            # Create variants and set the first one as the default variant
            
            default_variant = None
            for i, variant_payload in enumerate(variants_payload):
                is_default_variant = variant_payload.pop('is_default_variant', False)
                variant = ProductVariant.objects.create(
                    product=instance,
                    currency=currency,
                    **variant_payload
                )
                if is_default_variant:
                    default_variant = variant

            if default_variant:
                instance.default_variant = default_variant

            if tags_payload:
                for tag_payload in tags_payload:
                    tag, _ = ProductTag.objects.get_or_create(name=tag_payload)
                    instance.tags.add(tag)

            if instance.status == PublishableStatus.PUBLISHED:
                instance.is_live = True
            else:
                instance.is_live = False

            instance.save()
            
        return instance
    

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'

    
