from django.urls import path
from nxtbn.core.api.dashboard import views as core_views

urlpatterns = [
    path('/site-setting/<int:id>/', core_views.SiteSettingView.as_view(), name='site-setting')
]
