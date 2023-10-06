from django.db import models
from db.orders import OrderVars
from db.account.models import Customer
from db.helper_models import BaseModel
from db.orders.models import SalesOrder
from db.product.models import File

class OrderLog(BaseModel):
    order_type = models.CharField(max_length=128, choices=OrderVars.LOG_TYPES)
    data = models.JSONField()


class HelpDesk(BaseModel):
    client = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    files = models.ManyToManyField(File, related_name="desks", blank=True)
    orders = models.ManyToManyField(SalesOrder, related_name="desks", blank=True)

    uid = models.CharField(max_length=128, unique=True)
    status = models.CharField(max_length=24)
    order_date = models.DateTimeField(null=True)
    shipment_service = models.CharField(max_length=128, null=True)
    tracking_code = models.CharField(max_length=128, null=True)
    notes = models.TextField(null=True)
    comment = models.TextField(null=True)

    def __str__(self):
        return self.uid