from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
import simplejson as json

from db.helper_views import BaseModelsViewset, CustomTrashViewSet
from db.filters import ConditionFilter, DateFilter, EdgeDateFilter, PermissionFilter
from db.utils import compare_dicts
from db.permissions import CustomPermission

from . import models as product_models
from db.account.models import Translation

from . import serializers as product_serializers
from .tasks import upload_product_csv


class CategoryViewSet(CustomTrashViewSet):
    permission_classes = [CustomPermission]
    filter_backends = [OrderingFilter, ConditionFilter, DateFilter, EdgeDateFilter, PermissionFilter]
    date_filter_field = "created_at"
    ordering_fields = ["uid", "name", "description", "parent", "created_at"]
    model_class = product_models.ProductCategory
    serializer_class = product_serializers.ProductCategorySerializer
    queryset = model_class.objects.all()


class AttributeViewSet(BaseModelsViewset):
    permission_classes = [IsAdminUser]
    filter_backends = [OrderingFilter, ConditionFilter, DateFilter]
    date_filter_field = "created_at"
    ordering_fields = ["name", "description", "created_at"]
    model_class = product_models.ProductAttribute
    serializer_class = product_serializers.AttributeSerializer
    queryset = model_class.objects.all()


class TagViewSet(BaseModelsViewset):
    permission_classes = [IsAdminUser]
    filter_backends = [OrderingFilter, ConditionFilter, DateFilter]
    date_filter_field = "created_at"
    ordering_fields = ["name", "description", "created_at"]
    serializer_class = product_serializers.TagSerializer
    model_class = product_models.ProductTag
    queryset = model_class.objects.all()


class ProductViewSet(CustomTrashViewSet):
    permission_classes = [CustomPermission]
    filter_backends = [OrderingFilter, ConditionFilter, DateFilter, EdgeDateFilter, PermissionFilter]
    date_filter_field = "created_at"
    ordering_fields = ["sku", "title", "purchase_price", "created_at"]
    serializer_class = product_serializers.ProductSerializer
    model_class = product_models.Product
    queryset = model_class.objects.all()

    @action(methods=["post"], detail=False)
    def upload_csv(self, request):
        upload_product_csv(request)
        return Response("ok")

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.prefetch_related("alternate_images").prefetch_related("exp")

    def update(self, request, *args, **kwargs):
        product = self.get_object()
        extra_data = product.extra_data
        product_exp = product.exp.all()
        images = product.alternate_images
        tags = product.tags

        if new_extra := request.data.pop("extra_data", None):
            if extra_data:
                update_fields = compare_dicts(extra_data.__dict__, new_extra)
                product_models.ProductData.objects.filter(id=extra_data.id).update(**update_fields)
            else:
                product_models.ProductData.objects.create(product_id=product.id, **extra_data)
        else:
            if extra_data:
                extra_data.delete()

        if new_alternate := request.data.pop("alternate_images", None):
            product.alternate_images.clear()
            product.alternate_images.add(*new_alternate)

        updated_exp_ids = []
        if new_exp_ls := request.data.pop("exp", []):
            for new_exp in new_exp_ls:
                new_exp["product"] = product.id
                serializer = product_serializers.QualityDataSerializer(data=new_exp)
                if not serializer.is_valid():
                    return Response(status=400, data=serializer.errors)
                if update_exp := product_exp.filter(quality_text=new_exp["quality_text"]):
                    updated_exp_ids.append(serializer.custom_update(update_exp).id)
                else:
                    updated_exp_ids.append(serializer.save().id)

        product.exp.exclude(id__in=updated_exp_ids).delete()

        if new_tags := request.data.pop("tags", []):
            tags.clear()
            tags.add(*new_tags)

        update_fields = compare_dicts(product.__dict__, request.data)
        instance = product_models.Product.objects.filter(id=product.id)
        instance.update(**update_fields)
        serializer = self.get_serializer(instance.first()).data
        return Response(data=serializer)


class ProductServiceViewSet(BaseModelsViewset):
    permission_classes = [IsAdminUser]
    filter_backends = [OrderingFilter, ConditionFilter]
    ordering_fields = [
        "name",
        "description",
        "purchase_price",
        "price_gross",
        "price_net",
        "price_tax",
        "account",
        "created_at",
    ]
    serializer_class = product_serializers.ProductServiceSerializer
    model_class = product_models.ProductService
    queryset = model_class.objects.all()