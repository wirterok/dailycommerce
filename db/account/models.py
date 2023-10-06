from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Permission, Group
from django.utils.translation import gettext_lazy as _
from db.helper_models import BaseModel, Permission, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from db.core.models import Token
import uuid

class Translation(models.Model):
    lang = models.CharField(max_length=24)
    name = models.CharField(max_length=128)
    description = models.TextField(null=True)
    assigned_to = models.CharField(max_length=24)

    class Meta:
        unique_together = ["lang", "name", "assigned_to"]


class Address(BaseModel):
    street = models.CharField(max_length=256)
    street_number = models.CharField(max_length=16, blank=True, default=True)
    zip = models.CharField(max_length=24)
    city = models.CharField(max_length=64)
    country = models.CharField(max_length=64, blank=True, default="")
    key = models.CharField(max_length=128, null=True, blank=True)
    location_name = models.CharField(max_length=128, null=True, blank=True)
    location_ID = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f"{self.country} -> {self.city} -> {self.street} -> {self.street_number}" 


class CustomerGroup(Group):
    pass


class CustomerPermission(Permission):
    group = models.ForeignKey(CustomerGroup, on_delete=models.CASCADE, null=True, related_name="permissions")


class Customer(AbstractUser):
    id = models.CharField(max_length=128, primary_key=True, editable=False, default=uuid.uuid4)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128, null=True)
    phone = models.CharField(max_length=24, null=True, blank=True)
    name = models.CharField(max_length=256, null=True, blank=True)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    status = models.CharField(max_length=128, null=True)
    avatar = models.ImageField(upload_to="user-avatars", null=True)
    lang = models.CharField(max_length=16, default="en-GB", null=True)
    payment_account = models.CharField(max_length=128, null=True)
    is_confirmed = models.BooleanField(null=True, default=False)
    street = models.CharField(max_length=256)
    street_number = models.CharField(max_length=16, blank=True, default=True)
    zip = models.CharField(max_length=24)
    city = models.CharField(max_length=64)
    country = models.CharField(max_length=64, blank=True, default="")
    tenant_id = models.IntegerField()
    groups = models.ForeignKey(CustomerGroup, on_delete=models.CASCADE, null=True)
    user_permissions = models.ManyToManyField(CustomerPermission, blank=True)

    def __str__(self):
        return self.username

    # def save(self, force_insert=False, force_update=False, request=None, *args, **kwargs):
    #     if request:
    #         self.tenant_id = request.tenant_id
    #     super().save(force_insert, force_update, *args, **kwargs)
        

@receiver(post_save, sender=Customer)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance.id, tenant_id=instance.tenant_id) 