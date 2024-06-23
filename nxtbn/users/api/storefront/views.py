from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate
from allauth.account import app_settings as allauth_settings
from allauth.account.utils import complete_signup
from allauth.account.models import EmailAddress

from nxtbn.users.api.storefront.serializers import (
    JwtBasicUserSerializer,
    LoginRequestSerializer,
    RefreshSerializer,
    SignupSerializer,
)
from nxtbn.users.utils.jwt_utils import JWTManager


class SignupView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SignupSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.jwt_manager = JWTManager()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        complete_signup(request._request, user, allauth_settings.EMAIL_VERIFICATION, None)

        response_data = {"detail": _("Verification e-mail sent. Please check your email.")}

        if allauth_settings.EMAIL_VERIFICATION != allauth_settings.EmailVerificationMethod.MANDATORY:
            access_token = self.jwt_manager.generate_access_token(user)
            refresh_token = self.jwt_manager.generate_refresh_token(user)

            user_data = JwtBasicUserSerializer(user).data
            response_data = {
                "user": user_data,
                "token": {
                    "access": access_token,
                    "refresh": refresh_token,
                },
            }

        return Response(response_data, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginRequestSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.jwt_manager = JWTManager()

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(email=email, password=password)
        if user:
            email_verification_required = (
                allauth_settings.EMAIL_VERIFICATION == allauth_settings.EmailVerificationMethod.MANDATORY
            )
            email_verified = EmailAddress.objects.filter(user=user, verified=True).exists()

            if email_verification_required and not email_verified:
                return Response(
                    {"detail": _("Email not verified. Please verify your email.")},
                    status=status.HTTP_403_FORBIDDEN,
                )

            access_token = self.jwt_manager.generate_access_token(user)
            refresh_token = self.jwt_manager.generate_refresh_token(user)

            user_data = JwtBasicUserSerializer(user).data
            return Response(
                {
                    "user": user_data,
                    "token": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response({"detail": _("Invalid credentials")}, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RefreshSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.jwt_manager = JWTManager()

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = request.data.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": _("Refresh token is required.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = self.jwt_manager.verify_jwt_token(refresh_token)

        if user:
            access_token = self.jwt_manager.generate_access_token(user)
            # The refresh token generation is currently omitted to avoid additional overhead 
            # since we have not implemented a token blacklist mechanism yet. 
            # This feature may be added in the future based on business requirements.
            # new_refresh_token = self.jwt_manager.generate_refresh_token(user)

            user_data = JwtBasicUserSerializer(user).data
            return Response(
                {
                    "user": user_data,
                    "token": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": _("Invalid or expired refresh token.")},
            status=status.HTTP_401_UNAUTHORIZED,
        )
