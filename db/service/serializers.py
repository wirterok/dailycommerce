from rest_framework import serializers
from .models import OrderLog, HelpDesk
from db.product.models import Product
from db.product.serializers import QualityDataSerializer
from db.orders.models import ProductUnit
from db.orders.serializers import SellingOrderSerializer
from db.account.serializers import CustomerSerializer
from db.utils import write_instance
import json


class OrderLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLog
        fields = ["data"]

    def to_representation(self, obj):
        data = super().to_representation(obj)
        data = json.loads(data["data"])
        return data


class TaskProduct(serializers.ModelSerializer):
    exp = QualityDataSerializer(many=True)

    class Meta:
        model = Product
        fields = ["id", "title", "description", "exp"]


class TaskItem(serializers.ModelSerializer):
    product = TaskProduct()
    class Meta:
        model = ProductUnit
        fields = ["id", "serial_num", "purchase_order", "product"]


class DeskSerializer(serializers.ModelSerializer):
    orders = SellingOrderSerializer(required=False, read_only=True)
    orders_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    files = serializers.SerializerMethodField(read_only=True)
    files_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    client = CustomerSerializer(required=False)

    class Meta:
        model = HelpDesk
        fields = "__all__"

    def save(self):
        files = self.validated_data.pop("files_ids", [])
        orders = self.validated_data.pop("orders_ids", [])
        client = self.validated_data.pop("client", [])

        instance = super().save()

        if files:
            instance.files.add(files)
        if orders:
            instance.orders.add(orders)
        if client:
            seller_instance = write_instance(data=client, serializer_class=CustomerSerializer, context=self.context)
            instance.seller = seller_instance
        return instance.save()

    def get_files(self, obj):
        images = obj.files.all()
        ls = [default_storage.url(str(obj.image)) for obj in images]
        return ls