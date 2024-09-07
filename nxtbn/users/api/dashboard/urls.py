from django.urls import path
from nxtbn.users.api.dashboard import views as users_views

urlpatterns = [
    path('login/', users_views.LoginView.as_view(), name='login'),
    path('token/refresh/', users_views.DashboardTokenRefreshView.as_view(), name='token_refresh'),
    path('customers/', users_views.CustomerListAPIView.as_view(), name='customer-list'),
    path('customers/<str:username>/', users_views.CustomerDetailView.as_view(), name='customer-detail'),
    path('users/', users_views.UserListAPIView.as_view(), name='user-list'),
    path('change-password/', users_views.PasswordChangeView.as_view(), name='change_password'),
]
