from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.filters import OrderingFilter

from . import models as payment_models
from .serializers import PaymentSerializer, AccountSerializer, PaymentAccountSerializer
from db.helper_views import BaseModelsViewset, CustomQuerysetViewSet, CustomTrashViewSet
from db.payment.tasks import upload_account_csv
from db.permissions import CustomPermission
from db.filters import ConditionFilter, DateFilter

# Create your views here.


class PaymentViewSet(CustomTrashViewSet):
    permission_classes = [IsAdminUser]
    filter_backends = [OrderingFilter, ConditionFilter, DateFilter]
    date_filter_field = "created_at"
    ordering_fields = ["id", "status", "created_at", "type", "amount", "name"]
    model_class = payment_models.Payment
    queryset = model_class.objects.all()
    serializer_class = PaymentSerializer


class AccountViewSet(BaseModelsViewset, CustomQuerysetViewSet):
    permission_classes = [IsAdminUser]
    filter_backends = [OrderingFilter]
    ordering_fields = [
        "name",
        "description",
        "account_number",
        "account_type",
        "account_cost",
        "account_profit",
        "default_for",
        "created_at",
    ]
    model_class = payment_models.Account
    queryset = model_class.objects.all()
    serializer_class = AccountSerializer

    @action(methods=["get"], detail=False)
    def debitors(self, request):
        qs = super().get_queryset()
        ids = qs.prefetch_related("sale_orders").filter(sale_orders__isnull=False).values_list("id", flat=True)
        qs = qs.filter(id__in=ids)
        return self.get_list(qs)

    @action(methods=["get"], detail=False)
    def creditors(self, request):
        qs = super().get_queryset()
        ids = qs.prefetch_related("purchase_orders").filter(purchase_orders__isnull=False).values_list("id", flat=True)
        qs = qs.filter(id__in=ids)
        return self.get_list(qs)

    @action(methods=["post"], detail=False)
    def upload_csv(self, request):
        upload_product_csv(request)
        return Response("ok")

    @action(methods=["post"], detail=False)
    def upload_csv(self, request):
        upload_account_csv(request)
        return Response("ok")


class PaymentAccountViewSet(BaseModelsViewset):
    permission_classes = [IsAdminUser]
    filter_backends = [OrderingFilter]
    ordering_fields = ["name", "description", "account__account_number", "number", "type", "opening_date", "created_at"]
    model_class = payment_models.PaymentAccount
    queryset = model_class.objects.all()
    serializer_class = PaymentAccountSerializer