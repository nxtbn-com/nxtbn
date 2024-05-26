from django.urls import path
from nxtbn.core.api.dashboard import views as core_views

urlpatterns = [
    path('pluggin-install-via-git/', core_views.PlugginsInstallViaGitView.as_view(), name='upload_pluggins_via_git'),
    path('upload-pluggins/', core_views.PlugginsUploadView.as_view(), name='upload_pluggins'),
    
]
