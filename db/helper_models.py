from django.db import models
from db.core import PermissionsTypes
import datetime


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now=False)
    updated_at = models.DateTimeField(auto_now=True)
        
    def save(self, force_insert=False, force_update=False, request=None, *args, **kwargs):
        if self._state.adding:
            self.created_at = datetime.datetime.now()

        super().save(force_insert, force_update, *args, **kwargs)

    class Meta:
        abstract = True


class Group(models.Model):
    name_EN = models.CharField(max_length=128, default="")
    name_DE = models.CharField(max_length=128, default="")
    description_EN = models.TextField(null=True)
    description_DE = models.TextField(null=True)
    discipline_EN = models.CharField(max_length=64, null=True)
    discipline_DE = models.CharField(max_length=64, null=True)
    network_manager = models.BooleanField(default=True)
    
    class Meta:
        abstract = True


class Permission(models.Model):
    model_name = models.CharField(max_length=64)
    rights = models.CharField(max_length=24, choices=PermissionsTypes.PermissionChoices)
    
    class Meta:
        abstract = True


