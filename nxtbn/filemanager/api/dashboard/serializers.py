from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from nxtbn.filemanager.models import Image, Document


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_by",
            "last_modified_by",
        )

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        validated_data["last_modified_by"] = self.context["request"].user
        return super().create(validated_data)


class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_by",
            "last_modified_by",
        )

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        validated_data["last_modified_by"] = self.context["request"].user
        return super().create(validated_data)
