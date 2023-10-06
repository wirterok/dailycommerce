from db.helper_serializers import BaseTranslateSerializer
from .models import Warehouse, WarehouseStorage


class UnitSerializer(BaseTranslateSerializer):

    class Meta:
        model = WarehouseStorage
        fields = [
            "id",
            "name",
            "unit_id",
            "code"
        ]


class WarehouseSerializer(BaseTranslateSerializer):
    units = UnitSerializer(many=True)
    class Meta:
        model = Warehouse
        fields = [
            "id",
            "location_ID",
            "location_name",
            "created_at",
            "updated_at",
            "units",
            "translations"
        ]
        read_only_fields = ["created_at"]

    def save(self):
        if units := self.validated_data.get("units", []):
            units = self.validated_data.pop("units")

        instance = super().save()

        if units:
            for unit in units:
                self.process_unit(unit, instance)

    @staticmethod
    def process_unit(unit_data, wr_instance):
        qs = WarehouseStorage.objects.filter(unit_id=unit_data["unit_id"])
        if qs.exists():
            qs.first().update(**unit_data)
        else:
            unit_data["warehouse_id"] = wr_instance.id
            qs.create(**unit_data)