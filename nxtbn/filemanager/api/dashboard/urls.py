from django.urls import path
from nxtbn.filemanager.api.dashboard.views import ImageListView, ImageDetailView, DocumentListView, DocumentDetailView

urlpatterns = [
    path("images/", ImageListView.as_view(), name="image_list"),
    path("image/<int:id>/", ImageDetailView.as_view(), name="image_detail"),
    path("documents/", DocumentListView.as_view(), name="document_list"),
    path("document/<int:id>/", DocumentDetailView.as_view(), name="document_detail"),
]
