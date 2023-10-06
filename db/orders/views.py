from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.filters import OrderingFilter
from . import models as order_models
from . import serializers as order_serializers
from db.helper_views import BaseModelsViewset, CustomQuerysetViewSet, CustomTrashViewSet
from db.filters import ConditionFilter, DateFilter, EdgeDateFilter, PermissionFilter
from db.permissions import CustomPermission
from . import OrderVars, ExpenseVars
from .tasks import upload_purchase_order, upload_sales_order
from db.account.models import Customer
from db.utils import compare_dicts

# Create your views here.


class InvoiceViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    model_class = order_models.Invoice
    queryset = model_class.objects.all()
    serializer_class = order_serializers.PurchaseInvoiceSerializer


class SerializedViewSet(CustomTrashViewSet):
    permission_classes = [CustomPermission]
    filter_backends = [OrderingFilter, ConditionFilter, DateFilter, PermissionFilter]
    date_filter_field = "created_at"
    ordering_fields = ["id", "name", "status", "stock", "selling_price", "created_at"]
    model_class = order_models.ProductUnit
    queryset = model_class.objects.all()
    serializer_class = order_serializers.ProductUnitSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(enabled=True)


class PurchaseViewSet(CustomTrashViewSet):
    permission_classes = [CustomPermission]
    filter_backends = [OrderingFilter, ConditionFilter, DateFilter, EdgeDateFilter, PermissionFilter]
    date_filter_field = "created_at"
    ordering_fields = ["uid", "seller__email", "status", "total_price", "creditor_account", "payment", "order_date"]
    model_class = order_models.PurchaseOrder
    queryset = model_class.objects.all()
    serializer_class = order_serializers.PurchaseOrderSerializer

    @action(methods=["post"], detail=False)
    def upload_csv(self, request):
        upload_purchase_order(request)
        return Response("ok")

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.prefetch_related("serialized_products")

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        seller = order.seller
        serialized = order.serialized_products.all()

        if new_seller := request.data.pop("seller", None):
            new_seller.pop("password", None)
            Customer.objects.filter(id=seller.id).update(**new_seller)

        updated_item_ids = []
        if new_serialized := request.data.pop("serialized_products", None):
            for new_serialized_item in new_serialized:
                id = new_serialized_item.get("id")
                if id and order_models.ProductUnit.objects.filter(id=id):
                    serialized_qs = order_models.ProductUnit.objects.filter(id=id)
                    update_fields = compare_dicts(serialized_qs.first().__dict__, new_serialized_item)
                    serialized_qs.update(**update_fields)
                    updated_item_ids.append(id)
                else:
                    new_serialized_item["purchase_order"] = order.id
                    serializer = order_serializers.ProductUnitSerializer(
                        data=new_serialized_item, context={"request": request}
                    )
                    if not serializer.is_valid():
                        return Response(data=serializer.errors)
                    updated_item_ids.append(serializer.save().id)

        order.products.exclude(id__in=updated_item_ids).delete()

        if new_invoices := request.data.pop("invoices", None):
            order.invoices.clear()
            order.invoices.add(*new_invoices)

        update_fields = compare_dicts(order.__dict__, request.data)
        order_models.PurchaseOrder.objects.filter(id=order.id).update(**update_fields)
        serializer = self.get_serializer(self.get_object()).data
        return Response(data=serializer)


class SalesOrderViewSet(CustomTrashViewSet):
    permission_classes = [CustomPermission]
    filter_backends = [OrderingFilter, ConditionFilter, DateFilter, PermissionFilter]
    date_filter_field = "created_at"
    ordering_fields = ["id", "buyer__name", "status", "total_price", "created_at", "payment"]
    model_class = order_models.SalesOrder
    queryset = model_class.objects.all()
    serializer_class = order_serializers.SellingOrderSerializer

    @action(methods=["post"], detail=False)
    def upload_csv(self, request):
        upload_sales_order(request)
        return Response("ok")

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        buyer = order.buyer
        invoice = order.invoice
        serialized = order.products.all()

        if new_buyer := request.data.pop("seller", None):
            new_buyer.pop("password", None)
            Customer.objects.filter(id=buyer.id).update(**new_buyer)

        if new_invoice := request.data.pop("invoice", None):
            order_models.Invoice.filter(id=invoice.id).update(**new_invoice)

        updated_item_ids = []
        if new_serialized := request.data.pop("products", None):
            for new_serialized_item in new_serialized:
                id = new_serialized_item.get("id")
                if order_models.ProductUnit.objects.filter(id=id):
                    serialized_qs = order_models.ProductUnit.objects.filter(id=id)
                    update_fields = compare_dicts(serialized_qs.first().__dict__, new_serialized_item)
                    serialized_qs.update(**update_fields)
                else:
                    order_models.ProductUnit.objects.filter(id=id).update(sell_order_id=order.id)
                updated_item_ids.append(id)

        order.products.exclude(id__in=updated_item_ids).update(sell_order_id=None)

        update_fields = compare_dicts(order.__dict__, request.data)
        instance = order_models.SalesOrder.objects.filter(id=order.id).update(**update_fields).first()
        serializer = self.get_serializer(instance).data
        return Response(data=serializer.data, status=201)


class ExpenseSupplierViewSet(BaseModelsViewset):
    permission_classes = [IsAdminUser]
    filter_backends = [OrderingFilter]
    ordering_fields = ["company_name", "street", "zip", "city", "country", "tax_id", "account"]
    model_class = order_models.ExpenseSupplier
    queryset = model_class.objects.all()
    serializer_class = order_serializers.ExpenseSupplierSerializer


class ExpenseViewSet(CustomTrashViewSet):
    permission_classes = [CustomPermission]
    filter_backends = [OrderingFilter, ConditionFilter, DateFilter]
    date_filter_field = "created_at"
    ordering_fields = ["id", "created_at", "date", "invoice__id", "supplier__name", "total_price"]
    model_class = order_models.Expense
    queryset = model_class.objects.all()
    serializer_class = order_serializers.ExpenseSerializer

    def update(self, request):
        expense = self.get_object()

        updated_item_ids = []
        if new_items := request.data.pop("items", None):
            for item in new_items:
                id = item.get("id")
                if order_models.ExpenseItem.objects.filter(id=id):
                    qs = order_models.ExpenseItem.objects.filter(id=id)
                    update_fields = compare_dicts(qs.first().__dict__, item)
                    qs.update(**update_fields)
                    updated_item_ids.append(id)
                else:
                    item["expense"] = order.id
                    serializer = order_serializers.ExpenseItemSerializer(data=item, context={"request": request})
                    if not serializer.is_valid():
                        return Response(data=serializer.errors)
                    updated_item_ids.append(serializer.save().id)

        order.expense_items.exclude(id__in=updated_item_ids).update(sell_order_id=None)

        update_fields = compare_dicts(expense.__dict__, request.data)
        instance = order_models.Expense.objects.filter(id=order.id).update(**update_fields).first()
        serializer = self.get_serializer(instance).data
        return Response(data=serializer.data, status=201)


class ExpenseItemViewSet(BaseModelsViewset):
    model_class = order_models.ExpenseItem
    queryset = model_class.objects.all()
    serializer_class = order_serializers.ExpenseItemSerializer
