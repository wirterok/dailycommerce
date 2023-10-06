from db.product.models import File
from rest_framework import serializers

from rest_framework.authentication import TokenAuthentication
from rest_framework import permissions


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ["id", "file"]