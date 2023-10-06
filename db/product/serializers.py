from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.db.models import Subquery, OuterRef, F
import simplejson as json

from db.helper_serializers import BaseTranslateSerializer
from db.payment.models import Account
from db.payment.serializers import AccountSerializer
from db.serializers import FileSerializer

from db.utils import get_ids

from . import models as product_models


class ProductCategorySerializer(BaseTranslateSerializer):
    avatar_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = product_models.ProductCategory
        fields = [
            "id",
            "translations",
            "avatar_url",
            "uid",
            "name",
            "description",
            "created_at",
            "updated_at",
            "user_owner",
        ]
        read_only_fields = ["user_owner", "created_at"]

    def get_avatar_url(self, obj):
        if obj.avatar:
            return default_storage.url(str(obj.avatar))

    def save(self):
        instance = super().save()
        instance.user_owner = self.context["request"].user.id
        return instance.save()


class AttributeSerializer(BaseTranslateSerializer):
    class Meta:
        model = product_models.ProductAttribute
        fields = ["id", "name", "description", "terms", "translations", "terms", "created_at", "updated_at"]
        read_only_fields = ["created_at"]

    def is_valid(self, raise_exception=False):
        if terms := self.initial_data.get("terms", []):
            terms = json.dumps(terms)
        else:
            terms = json.dumps([])

        self.initial_data["terms"] = terms
        super().is_valid(raise_exception)

    def to_representation(self, obj):
        data = super().to_representation(obj)
        json_dec = json.decoder.JSONDecoder()
        data["terms"] = json_dec.decode(data["terms"])
        return data


class TagSerializer(BaseTranslateSerializer):
    class Meta:
        model = product_models.ProductTag
        fields = ["id", "name", "description", "created_at", "translations"]
        extra_kwargs = {"description": {"default": ""}}
        read_only_fields = ["created_at"]


class QualityDataSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True, read_only=True)
    files_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=product_models.Product.objects.all())

    class Meta:
        model = product_models.QualityData
        fields = ["quality_text", "quality_description", "files", "files_ids", "product"]
        extra_kwargs = {"quality_description": {"default": ""}}

    def get_images(self, obj):
        images = obj.files.all()
        ls = [default_storage.url(str(obj.image)) for obj in images]
        return ls

    def save(self):
        images = self.validated_data.pop("files_ids", [])
        quality_qs = product_models.QualityData.objects.filter(
            quality_text=self.validated_data["quality_text"],
            quality_description=self.validated_data["quality_description"],
        )
        if quality_qs.exists():
            quality_qs.update(**self.validated_data)
            instance = quality_qs.first()
        else:
            instance = super().save()
        if images:
            instance.files.add(*images)

        return instance

    def custom_update(self, qs):
        images = self.validated_data.pop("files_ids", [])
        self.validated_data.pop("product", None)

        qs.update(**self.validated_data)
        instance = qs.first()
        if images:
            instance.files.clear()
            instance.files.add(*images)

        return instance


class ExtraDataSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = product_models.ProductData
        fields = "__all__"
        extra_kwargs = {"product": {"required": False, "allow_null": True}}


class ProductAttributeSerializer(serializers.Serializer):
    name = serializers.CharField()
    term = serializers.CharField()


class ProductSerializer(BaseTranslateSerializer):
    attributes = ProductAttributeSerializer(many=True, required=False)
    alternate_images = FileSerializer(many=True, read_only=True)
    exp = QualityDataSerializer(many=True, required=False)
    tags = TagSerializer(many=True, required=False)
    extra_data = ExtraDataSerializer(many=False, required=False)

    files_ids = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)

    class Meta:
        model = product_models.Product
        fields = [
            "id",
            "title",
            "sku",
            "purchase_price",
            "marketplace_sku",
            "tags",
            "attributes",
            "exp",
            "alternate_images",
            "extra_data",
            "translations",
            "files_ids",
            "user_owner",
        ]
        read_only_fields = ["user_owner"]

    # def get_alternate_images(self, obj):
    #     qs = obj.alternate_images.all()
    #     ls = [default_storage.url(str(obj.image)) for obj in qs]
    #     return ls

    def save(self):
        images = self.validated_data.pop("files_ids", [])
        tags = self.validated_data.pop("tags", [])
        exp = self.validated_data.pop("exp", [])
        extra_data = self.validated_data.pop("extra_data", {})

        instance = super().save()

        if images:
            instance.alternate_images.add(*images)
        if tags:
            tags_ids = get_ids(product_models.ProductTag, tags, ["name"])
            instance.tags.add(*tags_ids)
        if exp:
            write_instance(
                data=exp,
                serializer_class=QualityDataSerializer,
                many=True,
                extra_field="product",
                extra_field_value=instance.id,
            )

        if extra_data:
            extra_data["product_id"] = instance.id
            serializer = ExtraDataSerializer(data=extra_data)
            if not serializer.is_valid():
                raise ValidationError(serializer.errors)
            serializer.save()

        instance.user_owner = self.context["request"].user.id
        return instance.save()

    @staticmethod
    def process_extra_data(instance, extra_data):
        if instance.extra_data:
            extra_instance = instance.extra_data.update(**extra_data)
        else:
            extra_instance = product_models.ProductData.objects.create(**extra_data)
        instance.extra_data = extra_instance
        instance.save()


class ProductServiceSerializer(BaseTranslateSerializer):
    account = AccountSerializer(many=False, read_only=True)
    account_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = product_models.ProductService
        fields = [
            "id",
            "name",
            "description",
            "purchase_price",
            "price_gross",
            "price_net",
            "price_tax",
            "created_at",
            "account",
            "translations",
            "account_id",
        ]
        read_only_fields = ["created_at"]