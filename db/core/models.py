import binascii
import os
from django.db import models
from django.db import connection
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from db.helper_models import BaseModel, Permission, Group

class Tenant(BaseModel):
    company_name = models.CharField(max_length=128, unique=True)
    paid_until =  models.DateField(auto_now=True)
    on_trial = models.BooleanField(default=True)
    db_conf = models.JSONField()
    db_name = models.CharField(max_length=128)

    def __str__(self):
        return self.company_name

    def delete(self):
        with connection.cursor() as cursor:
            cursor.execute(f"DROP SCHEMA IF EXISTS {self.db_name}_schema CASCADE;")



class SuperuserGroup(Group):
    pass


class SuperuserPermission(Permission):
    group = models.ForeignKey(SuperuserGroup, on_delete=models.CASCADE, null=True, related_name="permissions")

    def __str__(self):
        return f"{self.model_name} -> {self.rights}" 

class Superuser(AbstractUser, BaseModel):
    id = models.CharField(max_length=128, primary_key=True, editable=False, default=uuid.uuid4)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    status = models.CharField(max_length=128, null=True)
    avatar = models.ImageField(upload_to="user-avatars", null=True, blank=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=128, null=True)
    lang = models.CharField(max_length=16, default="en-GB", null=True)
    phone = models.CharField(max_length=24)
    is_confirmed = models.BooleanField(default=False)
    groups = models.ForeignKey(SuperuserGroup, on_delete=models.CASCADE, null=True)
    user_permissions = models.ManyToManyField(SuperuserPermission, blank=True)

    def __str__(self):
        return self.username


class Token(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    user = models.CharField(max_length=128)
    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key
    

@receiver(post_save, sender=Superuser)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance.id, tenant=instance.tenant) 


