from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from nxtbn.users.api.dashboard.serializers import DashboardLoginSerializer
from nxtbn.users.api.storefront.serializers import JwtBasicUserSerializer
from nxtbn.users.api.storefront.views import TokenRefreshView
from nxtbn.users.utils.jwt_utils import JWTManager

class LoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = DashboardLoginSerializer

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
            if not user.is_staff:
                return Response({"detail": _("Only staff members can log in.")}, status=status.HTTP_403_FORBIDDEN)
                
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


class DashboardTokenRefreshView(TokenRefreshView):
    pass