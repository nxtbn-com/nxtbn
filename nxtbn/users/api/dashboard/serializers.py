from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.db import transaction
from nxtbn.users.models import User

class DashboardLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)



class JwtBasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(write_only=True, required=True)