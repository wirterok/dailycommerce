from django.db import models
import json

from db.account.models import Address, Customer
from db.helper_models import BaseModel
from db.payment.models import Account, Payment
from db.product.models import Product, ProductService, QualityData, File
from db.warehouse.models import WarehouseStorage
from db.local_settings.models import Tax
from model_utils import FieldTracker
from . import OrderVars, ExpenseVars



class Invoice(BaseModel):
    translations = models.ManyToManyField(
        'account.Translation', 
        related_name="invoices",
        null=True,
        blank=True
    )
    file = models.ForeignKey(File, on_delete=models.CASCADE, null=True)
    date = models.DateField(auto_now=True)
    num = models.CharField(max_length=128, unique=True)


class PurchaseOrder(BaseModel):
    seller = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name="sellers")
    translations = models.ManyToManyField(
        'account.Translation', 
        related_name="purchase_orders"
    )
    creditor_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="purchase_orders")
    user_owner = models.CharField(max_length=128)
    invoices = models.ManyToManyField(File, blank=True, related_name="purchase_orders")
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, related_name="purchase_orders")

    uid = models.CharField(max_length=64, unique=True)
    order_date = models.DateField(auto_now=True)
    total_price = models.DecimalField(max_digits=7, decimal_places=2)
    condition_details = models.CharField(max_length=256)
    tracking_code = models.CharField(max_length=256, null=True)
    shipment_service = models.CharField(max_length=128, null=True)
    shipment_label = models.CharField(max_length=64, null=True)
    enabled = models.BooleanField(default=True)
    status = models.CharField(max_length=64)
    is_locked = models.BooleanField(default=False)
    serial_num = models.CharField(max_length=64, null=True)
    type = models.CharField(max_length=36, null=True)
    in_trash = models.BooleanField(null=True, default=False)

    def __str__(self):
        return f"Purchase order #{self.uid}"

    def save(self, force_insert=False, force_update=False, request=None, *args, **kwargs):
        if request:
            self.user_owner = request.user.id

        super().save(force_insert, force_update, *args, **kwargs)


class SalesOrder(BaseModel):  
    translations = models.ManyToManyField(
        'account.Translation', 
        related_name="sales_orders",
        blank=True
    )  
    buyer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name="buyers")
    debitor_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="sale_orders")
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, related_name="sale_orders")
    user_owner = models.CharField(max_length=128)
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, related_name="sale_orders")
    services = models.ManyToManyField(ProductService, related_name="sale_orders", blank=True)

    key = models.CharField(max_length=64, null=True)
    uid = models.CharField(max_length=64, unique=True)
    note = models.TextField(null=True)
    cancellation = models.CharField(max_length=256, null=True)
    total_price = models.DecimalField(max_digits=7, decimal_places=2)
    marketplace_price = models.DecimalField(max_digits=7, decimal_places=2, default=0, null=True)
    shipping_price = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    marketplace = models.CharField(max_length=128, null=True)
    tracking_code = models.CharField(max_length=256, null=True)
    shipment_service = models.CharField(max_length=128, null=True)
    shipment_label = models.CharField(max_length=64, null=True)
    shipment_status = models.CharField(max_length=64, null=True)
    enabled = models.BooleanField(default=True)
    status = models.CharField(max_length=64)
    bookkeeping_status = models.CharField(max_length=64, null=True)
    is_locked = models.BooleanField(default=False)
    in_trash = models.BooleanField(null=True, default=False)
    
    invoice_date = models.DateTimeField(auto_now=True, null=True)
    tracker = FieldTracker()

    def __str__(self):
        return f"Sales order #{self.uid}"


    def save(self, force_insert=False, force_update=False, request=None, *args, **kwargs):
        if request:
            self.user_owner = request.user.id

        super().save(force_insert=False, force_update=False, *args, **kwargs)

        changed = self.tracker.changed()
        if changed:
            create_log(OrderVars.SELL_ORDER, self)


class ProductUnit(BaseModel):
    product = models.ForeignKey(Product, related_name="items", on_delete=models.CASCADE)
    translations = models.ManyToManyField('account.Translation', related_name="serialized")
    purchase_order = models.ForeignKey(PurchaseOrder, related_name="serialized_products", on_delete=models.CASCADE, null=True)  
    sell_order = models.ForeignKey(SalesOrder, related_name="products", on_delete=models.SET_NULL, null=True)
    unit = models.ForeignKey(WarehouseStorage, related_name="products", on_delete=models.CASCADE, null=True)
    
    user_owner = models.CharField(max_length=128)
    exp = models.ManyToManyField(QualityData, blank=True, related_name="serialized")
    vat = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True)
    invoice_template = models.TextField(null=True) #make fk later
    enabled = models.BooleanField(default=False)
    serial_num = models.CharField(max_length=128, unique=True, default="")
    stock = models.DecimalField(max_digits=7, decimal_places=2)
    status = models.CharField(max_length=64)
    selling_price = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    purchase_price = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    manufacturers_serial = models.CharField(max_length=128)
    in_trash = models.BooleanField(null=True, default=False)

    tracker = FieldTracker()

    def __str__(self):
        return f"{self.vat} | {self.product.title}"

    def save(self, force_insert=False, force_update=False, request=None, *args, **kwargs):
        if request:
            self.user_owner = request.user.id

        super().save(force_insert, force_update, *args, **kwargs)


class ExpenseSupplier(BaseModel):
    company_name = models.CharField(max_length=128)
    street = models.CharField(max_length=128, null=True)
    zip = models.CharField(max_length=48, null=True)
    city = models.CharField(max_length=128, null=True)
    country = models.CharField(max_length=128, null=True)
    tax_id = models.CharField(max_length=128, null=True)
    account = models.ForeignKey(Account, related_name="supplier", on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return self.company_name 


class ExpenseCategory(BaseModel):
    translations = models.ManyToManyField(
        "account.Translation", 
        related_name="expense_categories"
    )
    name = models.CharField(max_length=128)
    description = models.TextField()

    def __str__(self):
        return self.name


class Expense(BaseModel):
    translations = models.ManyToManyField(
        "account.Translation", 
        related_name="expenses"
    )
    payment = models.ForeignKey(Payment, related_name="expense", on_delete=models.SET_NULL, null=True)
    invoice = models.ForeignKey("orders.Invoice", related_name="expense", on_delete=models.SET_NULL, null=True)
    supplier = models.ForeignKey(ExpenseSupplier, related_name="expense", on_delete=models.CASCADE)
    expense_tag_category = models.ForeignKey(ExpenseCategory, related_name="expense", on_delete=models.SET_NULL, null=True)
    date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=64, unique=True)
    total_price = models.DecimalField(max_digits=7, decimal_places=2)
    #expense items
    bookkeeping_status = models.CharField(max_length=64)
    is_locked = models.BooleanField(default=True)
    in_trash = models.BooleanField(null=True, default=False)
    user_owner = models.CharField(max_length=128)

    def __str__(self):
        return self.uid

    def save(self, force_insert=False, force_update=False, request=None, *args, **kwargs):
        if request:
            self.user_owner = request.user.id

        super().save(force_insert, force_update, *args, **kwargs)


class ExpenseItem(BaseModel):
    translations = models.ManyToManyField(
        "account.Translation", 
        related_name="expense_items"
    )
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=128, null=True)
    description = models.TextField(null=True)
    amount = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    var_percent = models.FloatField(null=True)
    vat = models.CharField(max_length=16, choices=ExpenseVars.VAT_TYPES, default="")
    expense = models.ForeignKey(Expense, related_name="expense_items", on_delete=models.CASCADE)
    def __str__(self):
        return self.name