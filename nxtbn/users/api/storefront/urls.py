# urls.py
from django.urls import path

from nxtbn.users.api.storefront.views import LoginView, SignupView, TokenRefreshView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
     path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
