from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _


from rest_framework import serializers

from allauth.account import app_settings as allauth_settings
from allauth.utils import  generate_unique_username
from allauth.account.utils import assess_unique_email
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.account.models import EmailAddress

from allauth.account.forms import ResetPasswordForm # Allauth's which provide only alluth urls to reset password

from nxtbn.users.models import User

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text='Leave empty if no change needed',
        style={'input_type': 'password', 'placeholder': 'Password'}
    )
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'password')
        
    def validate_email(self, email):
        adapter = get_adapter()
        assessment = assess_unique_email(email)
        if assessment is True:
            # All good.
            pass
        elif assessment is False:
            # Fail right away.
            raise serializers.ValidationError(adapter.error_messages["email_taken"])
        else:
            assert assessment is None
            # self.account_already_exists = True
        return adapter.validate_unique_email(email)


    def create(self, validated_data):
        # Create record in User table
        instance = self.Meta.model(
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            username=generate_unique_username(
                [
                    validated_data.get('first_name'),
                    validated_data.get('last_name'),
                    validated_data.get('email'),
                ]
            ),
            #user_type = 'author' # Place more built-in or custom fields there: is_staff=True etc
        )
        instance.set_password(validated_data.get('password'))
        instance.save()
        request = request = self.context.get('request')
        setup_user_email(request, instance, [])
        return instance

    def save(self, request=None):
        # Must override it to save the request data by rest_auth
        return super().save()



class JwtBasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name',)


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

class RefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(write_only=True, required=True)