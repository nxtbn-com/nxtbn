from django.conf import settings
from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from nxtbn.core.paginator import NxtbnPagination
from nxtbn.users import UserRole
from nxtbn.users.models import User
from nxtbn.users.api.dashboard.serializers import CustomerSerializer, DashboardLoginSerializer, UserSerializer
from nxtbn.users.api.dashboard.serializers import DashboardLoginSerializer, PasswordChangeSerializer
from nxtbn.users.api.storefront.serializers import JwtBasicUserSerializer
from nxtbn.users.api.storefront.views import TokenRefreshView
from nxtbn.users.utils.jwt_utils import JWTManager
from nxtbn.users.models import User
from nxtbn.core.admin_permissions import NxtbnAdminPermission

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
                    'store_url': settings.STORE_URL,
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


#=========================================
# Authentication related views end here
#=========================================

class CustomerListAPIView(generics.ListAPIView):
    """
    API view to retrieve the list of customers (users with role 'CUSTOMER').
    """
    serializer_class = CustomerSerializer
    pagination_class = NxtbnPagination

    def get_queryset(self):
        return User.objects.filter(role=UserRole.CUSTOMER)


class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API View to retrieve customer details
    """
    serializer_class = CustomerSerializer
    lookup_field = 'username'

    def get_queryset(self):
        return User.objects.filter(role=UserRole.CUSTOMER)
    

class UserListAPIView(generics.ListAPIView):
    """
    API view to retrieve the list of all users.
    """
    serializer_class = UserSerializer
    pagination_class = NxtbnPagination

    def get_queryset(self):
        return User.objects.all()

class PasswordChangeView(generics.UpdateAPIView):
    serializer_class = PasswordChangeSerializer
    model = User
    permission_classes = [NxtbnAdminPermission]

    def get_object(self, queryset=None):
        return self.request.user

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Set the new password
            serializer.save()
            return Response('Password changed successfully', status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


