from django.db import models

from db.account.models import Translation
from db.helper_models import BaseModel

class Warehouse(BaseModel):
    #units = serialized - serializer
    translations = models.ManyToManyField(
        Translation, 
        related_name="warehouses"
    )
    key = models.CharField(max_length=64)
    location_name = models.CharField(max_length=128)
    location_ID = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.location_ID} | {self.location_name}"


class WarehouseStorage(BaseModel):
    translations = models.ManyToManyField(
        Translation, 
        related_name="units"
    )
    warehouse = models.ForeignKey(Warehouse, related_name="units", on_delete=models.CASCADE)
    code = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    unit_id = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return f"{self.unit_id} | {self.name}"