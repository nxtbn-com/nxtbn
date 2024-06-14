from django.urls import path
from nxtbn.plugins.api.dashboard import views as plugins_views

urlpatterns = [
    path('pluggin-install-via-git/', plugins_views.PlugginsInstallViaGitView.as_view(), name='upload_pluggins_via_git'),
    path('upload-pluggins/', plugins_views.PlugginsUploadView.as_view(), name='upload_pluggins'),
    path('plugin-install-via-zip-url/', plugins_views.PluginInstallViaZipUrlView.as_view(), name='upload_pluggins_via_zip_url'),
    
]
