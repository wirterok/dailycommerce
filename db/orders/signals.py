from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PurchaseOrder, SalesOrder
from .serializers import PurchaseOrderSerializer, SellingOrderSerializer
from db.service.models import OrderLog
from db.orders import OrderVars
import json


def create_log(order, order_type, serializer):
    data = serializer(order).data
    json_data = json.dumps(data, indent=4)
    OrderLog.objects.create(order_type=order_type, data=json_data)


# @receiver(post_save, sender=PurchaseOrder)
# def create_purchase_order_log(sender, **kwargs):
#     obj = kwargs['instance']
#     create_log(obj, OrderVars.PURCHASE_ORDER, PurchaseOrderSerializer)


# @receiver(post_save, sender=SalesOrder)
# def create_sell_order_log(sender, **kwargs):
#     obj = kwargs['instance']
#     create_log(obj, OrderVars.SELL_ORDER, SellingOrderSerializer)