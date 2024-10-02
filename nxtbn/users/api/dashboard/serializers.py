from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.db import transaction
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q

from nxtbn.order import AddressType
from nxtbn.order.api.storefront.serializers import AddressSerializer
from nxtbn.users.admin import User


class DashboardLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'avatar', 'username', 'email', 'first_name', 'last_name', 'role', 'designation', 'phone_number']


class CustomerSerializer(serializers.ModelSerializer):
    default_shipping_address = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'avatar', 'username', 'email', 'first_name', 'last_name', 'full_name', 'phone_number', 'role', 'designation', 'default_shipping_address']

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

