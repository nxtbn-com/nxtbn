from rest_framework import generics
from django.utils.translation import gettext_lazy as _


from nxtbn.filemanager.models import Document, Image
from nxtbn.filemanager.api.dashboard.serializers import (
    DocumentSerializer,
    ImageSerializer,
)
from nxtbn.core.admin_permissions import NxtbnAdminPermission
from nxtbn.core.paginator import NxtbnPagination


class ImageListView(generics.ListCreateAPIView):
    serializer_class = ImageSerializer
    queryset = Image.objects.all()
    pagination_class = NxtbnPagination
    permission_classes = (NxtbnAdminPermission,)


class ImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    pagination_class = NxtbnPagination
    permission_classes = (NxtbnAdminPermission,)
    lookup_field = "id"


class DocumentListView(generics.ListCreateAPIView):
    serializer_class = DocumentSerializer
    queryset = Document.objects.all()
    permission_classes = (NxtbnAdminPermission,)
    pagination_class = NxtbnPagination


class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    pagination_class = NxtbnPagination
    permission_classes = (NxtbnAdminPermission,)
    lookup_field = "id"
