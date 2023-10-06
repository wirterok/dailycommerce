from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType

from .serializers import OrderLogSerializer, TaskItem, DeskSerializer
from .models import OrderLog, HelpDesk
from db.orders import OrderVars
from db.helper_views import BaseModelsViewset, CustomQuerysetViewSet
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from db.product.models import Product, ProductCategory
from db.product.serializers import ProductSerializer, ProductCategorySerializer
from db.orders.models import ProductUnit, PurchaseOrder, SalesOrder, Expense
from db.orders.serializers import (
    ProductUnitSerializer,
    PurchaseOrderSerializer,
    SellingOrderSerializer,
    ExpenseSerializer,
)
from db.payment.models import Payment
from db.payment.serializers import PaymentSerializer
from db.permissions import CustomPermission

import pandas as pd
from db.db_utils import bulk_upsert

class TrashViewSet(CustomQuerysetViewSet):
    permission_classes = [IsAdminUser]
    @action(methods=["get"], detail=False)
    def restore_all(self, request):
        qs = super().get_queryset()
        qs.update(in_trash=False)
        return Response(data={"msg": "Restored!"})

    @action(methods=["get"], detail=False)
    def delete_all(self, request):
        qs = super().get_queryset()
        qs.delete()
        return Response(data={"msg": "Deleted!"})

    @action(methods=["get"], detail=False)
    def restore(self, request):
        ids = request.data.get("id", [])
        ids = json.loads(ids)
        qs = super().get_queryset()
        qs.filter(id__in=ids).update(in_trash=False)
        return Response(data={"msg": "Restored!"})

    @action(methods=["get"], detail=False)
    def delete(self, request):
        ids = request.data.get("id", [])
        ids = json.loads(ids)
        qs = super().get_queryset()
        qs.filter(id__in=ids).delete()
        return Response(data={"msg": "Deleted!"})


class ProductTrashViewSet(TrashViewSet):
    model_class = Product
    queryset = model_class.objects.filter(in_trash=True)
    serializer_class = ProductSerializer


class CategoriesTrashViewSet(TrashViewSet):
    model_class = ProductCategory
    queryset = model_class.objects.filter(in_trash=True)
    serializer_class = ProductCategorySerializer


class InventoryTrashViewSet(TrashViewSet):
    model_class = ProductUnit
    queryset = model_class.objects.filter(in_trash=True)
    serializer_class = ProductUnitSerializer


class PurchaseOrderTrashViewSet(TrashViewSet):
    model_class = PurchaseOrder
    queryset = model_class.objects.filter(in_trash=True)
    serializer_class = PurchaseOrderSerializer


class SellOrderTrashViewSet(TrashViewSet):
    model_class = SalesOrder
    queryset = model_class.objects.filter(in_trash=True)
    serializer_class = SellingOrderSerializer


class PaymentTrashViewSet(TrashViewSet):
    model_class = Payment
    queryset = model_class.objects.filter(in_trash=True)
    serializer_class = PaymentSerializer


class ExpenseTrashViewSet(TrashViewSet):
    model_class = Expense
    queryset = model_class.objects.filter(in_trash=True)
    serializer_class = ExpenseSerializer


class PurchaseOrderLogViewSet(BaseModelsViewset):
    model_class = PurchaseOrder
    queryset = model_class.objects.all()
    serializer_class = PurchaseOrderSerializer


class SellOrderLogView(BaseModelsViewset):
    model_class = SalesOrder
    queryset = model_class.objects.all()
    serializer_class = SellingOrderSerializer
    filter_backends = []


class TaskView(GenericViewSet, ListModelMixin):
    permission_classes = [CustomPermission]
    queryset = PurchaseOrder.objects.filter(status="contract_signed")
    serializer_class = TaskItem

    def list(self, request):
        not_found_msg = {"msg": "Items with passed parameters was not found"}
        if seller := request.query_params.get("seller"):
            qs = PurchaseOrder.objects.filter(seller__name=seller)
            if qs.exists():
                items = qs.first().serialized_products
                data = TaskItem(items, many=True).data
                return Response(data=data)
            return Response(status=404, data=not_found_msg)

        if code := request.query_params.get("tracking_code"):
            qs = PurchaseOrder.objects.filter(tracking_code=code)
            if qs.exists():
                items = qs.first().serialized_products
                data = TaskItem(items, many=True).data
                return Response(data=data)
            return Response(status=404, data=not_found_msg)

        if pid := request.query_params.get("order_id"):
            qs = PurchaseOrder.objects.filter(id=pid)
            if qs.exists():
                items = qs.first().serialized_products
                data = TaskItem(items, many=True).data
                return Response(data=data)
            return Response(status=404, data=not_found_msg)

        return Response(
            status=400, data={"msg": "You shoukd provide any of parameters(order_id, tracking_code, seller)"}
        )

    @action(methods=["post"], detail=False)
    def accept(self, request):
        order_id = request.data.get("order_id")
        if not order_id:
            return Response(status=400, data="You should provide order id")

        try:
            order = super(TaskView, self).get_queryset().get(id=order_id)
        except:
            return Response(status=400, data="No such order. Maybe this order contract is not signed yet")

        order.status = "delivery_accepted"
        order.save()
        serialized_qs = order.serialized_products.all()
        serialized_qs.update(status="in_stock", enabled=True, in_trash=False)
        for serialized in serialized_qs:
            exp_ids = serialized.product.exp.values_list("id", flat=True)
            serialized.exp.add(*list(exp_ids))

        return Response("ok")

    @action(methods=["post"], detail=False)
    def decline(self, request):
        order_id = request.data.get("order_id")
        if not order_id:
            return Response(status=400, data="You should provide order id")

        try:
            order = super(TaskView, self).get_queryset().get(id=order_id)
        except:
            return Response(status=400, data="No such order. Maybe this order contract is not signed yet")
        order.status = "delivery_returned"
        order.save()
        serialized_qs = order.serialized_products.all()
        serialized_qs.update(status="in_trash", enabled=False, in_trash=True)
        return Response("Ok")


class HelpDeskViewset(ModelViewSet):
    permission_classes = [IsAdminUser]
    model_class = HelpDesk
    queryset = model_class.objects.all()
    serializer_class = DeskSerializer


# class OrderLogViewSet(CustomQuerysetViewSet):
#     model_class = OrderLog
#     queryset = model_class.objects.all()
#     serializer_class = OrderLogSerializer

#     @action(methods=["get"], detail=False)
#     def order_purchases(self, request):
#         qs = super().get_queryset()
#         qs = qs.filter(order_type=OrderVars.PURCHASE_ORDER)
#         return self.get_list(qs)

#     @action(methods=["get"], detail=False)
#     def order_sales(self, request):
#         qs = super().get_queryset()
#         qs = qs.filter(order_type=OrderVars.SELL_ORDER)
#         return self.get_list(qs)


@api_view(["post"])
def insert_backup(request):
    file = request.FILES.get("file")
    model_name = request.data.get("model")
    try:
        model = ContentType.objects.get(model=model_name)
    except:
        return Response("No model with passed name")
    model.objects.all().delete()
    upload_data = pd.read_json(file)
    bulk_upsert(
        model, 
        list(upload_data.columns),
        [tuple(x) for x in order_df.values.tolist()],
        f"{request.tenant.db_name}_schema",
        conflict_on=["id"],
        do_update=True,
        returning=["id"],
    )
    

@api_view(["post"])
def upload_backup(request):
    file = request.FILES.get("file")
    model_name = request.data.get("model")
    try:
        model = ContentType.objects.get(model=model_name)
    except:
        return Response("No model with passed name")

    upload_data = pd.read_json(file)
    bulk_upsert(
        model, 
        list(upload_data.columns),
        [tuple(x) for x in order_df.values.tolist()],
        f"{request.tenant.db_name}_schema",
        conflict_on=["id"],
        do_update=True,
        returning=["id"]
    )