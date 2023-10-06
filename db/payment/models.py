from django.db import models

from db.helper_models import BaseModel
from . import PaymentChoices

# Create your models here.

class Account(BaseModel):
    translations = models.ManyToManyField(
        'account.Translation', 
        related_name="accounts",
        null=True
    )
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(null=True)
    account_number = models.CharField(max_length=128, null=True)
    account_type = models.CharField(max_length=64, null=True)
    split_profit = models.BooleanField(default=False, null=True)
    account_cost = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    account_profit = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    default_for = models.CharField(max_length=64, null=True)

    def __str__(self):
        return f"{self.account_number} -> {self.name}"


class PaymentAccount(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="payment_accounts")
    translations = models.ManyToManyField(
        "account.Translation",
        related_name="payment_accounts",
        null=True
    )

    name = models.CharField(max_length=128)
    description = models.TextField(null=True)
    number = models.CharField(max_length=128)
    account_type = models.CharField(max_length=128)
    online = models.BooleanField(default=False, null=True)
    opening_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.name
    

class Payment(BaseModel):
    translations = models.ManyToManyField(
        'account.Translation', 
        related_name="payments",
        null=True
    )
    account = models.ForeignKey(PaymentAccount, related_name="payment", on_delete=models.CASCADE)
    receiver_account = models.CharField(max_length=128)
    status = models.CharField(max_length=64)
    type = models.CharField(max_length=24)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    name = models.CharField(max_length=128)
    description = models.TextField()
    note = models.CharField(max_length=128)
    marketplace_id = models.CharField(max_length=128, null=True, blank=True)
    bookkeeping_status = models.CharField(max_length=64, null=True, blank=True)
    is_locked = models.BooleanField(default=True, null=True, blank=True)
    in_trash = models.BooleanField(null=True, default=False)
    user_owner = models.CharField(max_length=128)
    
    def __str__(self):
        return f"{self.type} | {self.name}"

    def save(self, force_insert=False, force_update=False, request=None, *args, **kwargs):
        if request:
            self.user_owner = request.user.id

        super().save(force_insert, force_update, *args, **kwargs)
    