from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.db import transaction
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q

from nxtbn.order import AddressType
from nxtbn.order.api.storefront.serializers import AddressSerializer
from nxtbn.users import UserRole
from nxtbn.users.admin import User
from django.utils.crypto import get_random_string


class DashboardLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'avatar', 'username', 'email', 'first_name', 'last_name', 'role']


class CustomerSerializer(serializers.ModelSerializer):
    default_shipping_address = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'avatar', 'username', 'email', 'first_name', 'last_name', 'full_name', 'role', 'default_shipping_address']

    def get_default_shipping_address(self, obj):
        address = obj.addresses.filter(
            Q(address_type=AddressType.DSA) | Q(address_type=AddressType.DSA_DBA)
        ).first()
        return AddressSerializer(address).data if address else None


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, 
                                         #validators=[validate_password]
                                        )

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value

    def validate(self, attrs):
        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError(
                "New password cannot be the same as the old password"
            )
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user



class UserMututionalSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role', 'avatar', 'phone_number', 'is_active', 'is_staff', 'is_superuser', 'full_name', 'password']
        extra_kwargs = {
            'is_staff': {'read_only': True},
            'is_superuser': {'read_only': True},
            'role': {'read_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        
        # Set role to STAFF and is_superuser to False
        validated_data['role'] = UserRole.STAFF
        validated_data['is_superuser'] = False

        # Create user instance
        user = User(**validated_data)
        
        # If no password is provided, set a dummy password
        if password:
            user.set_password(password)
        else:
            user.set_password(get_random_string(8))
        
        user.save()
        return user

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr != 'password':
                setattr(instance, attr, value)
        
        instance.save()
        return instance
