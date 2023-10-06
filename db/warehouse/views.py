from django.shortcuts import render

from db.helper_views import BaseModelsViewset
from .models import Warehouse
from .serializers import WarehouseSerializer
from rest_framework.permissions import IsAdminUser
from rest_framework.filters import OrderingFilter

class WarehouseViewSet(BaseModelsViewset):
    permission_classes = [IsAdminUser]
    filter_backends = [OrderingFilter]
    ordering_fields = ["id", "name", "created_at"]
    model_class = Warehouse
    queryset = model_class.objects.all()
    serializer_class = WarehouseSerializer
    

