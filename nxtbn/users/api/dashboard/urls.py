from django.urls import path
from nxtbn.users.api.dashboard.views import LoginView, TokenRefreshView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh')
]
