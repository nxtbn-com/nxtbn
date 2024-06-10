from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions  import AllowAny
from rest_framework.exceptions import APIException
from django.contrib.auth import authenticate
from allauth.account.models import EmailAddress


from nxtbn.users.api.dashboard.serializers import DashboardLoginSerializer
from nxtbn.users.api.storefront.serializers import JwtBasicUserSerializer
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
        if user:
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