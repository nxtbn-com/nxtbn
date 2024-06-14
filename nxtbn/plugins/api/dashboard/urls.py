from django.urls import path
from nxtbn.plugins.api.dashboard import views as plugins_views

urlpatterns = [
    path('pluggin-install-via-git/', plugins_views.PlugginsInstallViaGitView.as_view(), name='upload_pluggins_via_git'),
    path('upload-pluggins/', plugins_views.PlugginsUploadView.as_view(), name='upload_pluggins'),
    path('plugin-install-via-zip-url/', plugins_views.PluginInstallViaZipUrlView.as_view(), name='upload_pluggins_via_zip_url'),
    path('plugin-details/<str:name>/', plugins_views.PluginDetailAPIView.as_view(), name='plugin_details'),
    path('unregistered-plugins/', plugins_views.UnregisteredPluginsAPIView.as_view(), name='unregistered-plugins'),
    path('register-plugin/', plugins_views.PluginRegisterView.as_view(), name='register-plugin'),

]
