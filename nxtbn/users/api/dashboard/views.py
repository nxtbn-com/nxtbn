from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions  import AllowAny
from rest_framework.exceptions import APIException
from django.contrib.auth import authenticate
from allauth.account.models import EmailAddress

from nxtbn.users.api.dashboard.serializers import DashboardLoginSerializer, RefreshTokenSerializer, JwtBasicUserSerializer
from nxtbn.users.utils.jwt_utils import generate_access_token, generate_refresh_token


class LoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = DashboardLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)


        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(email=email, password=password)
        
        if user and user.is_superuser:
            access_token = generate_access_token(user)
            refresh_token = generate_refresh_token(user)

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
    serializer_class = RefreshTokenSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        refresh_token = request.data.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": _("Refresh token is required.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = verify_jwt_token(refresh_token)

        if user and user.is_superuser:
            access_token = generate_access_token(user)
            refresh_token = generate_refresh_token(user)

            user_data = JwtBasicUserSerializer(user).data
            return Response(
                {
                    "user": user_data,
                    "token": {
                        "access": access_token,
                        # "refresh": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": _("Invalid or expired refresh token.")},
            status=status.HTTP_401_UNAUTHORIZED,
        )
