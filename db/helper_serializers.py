from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from db.account.models import Translation
from db.utils import write_instance

class TranslationSerializer(ModelSerializer):
    class Meta:
        model = Translation
        fields = [
            "lang",
            "name",
            "description"
        ]


class BaseTranslateSerializer(ModelSerializer):
    translations = TranslationSerializer(many=True, required=False, read_only=True)


class GroupSerializer(ModelSerializer):
    
    def validate(self, attrs):
        all_models_names = ContentType.objects.values_list("model", flat=True)
        group_permissions = attrs.pop("group_permissions", {})
        
        permissions = []
        for x in list(group_permissions.keys()):
            if x in all_models_names:
                permission_data = {
                    "model_name": x,
                    "rights": group_permissions[x]
                }
                validated_permission_data = self.validate_permission(permission_data)
                permissions.append(validated_permission_data)
                group_permissions.pop(x)
        attrs["permissions"] = permissions
        return attrs

    def save(self):
        permissions = self.validated_data.pop("permissions", [])
        instance = super().save()
        if permissions:
            write_instance(
                data=permissions, 
                serializer_class=self.Meta.permission_serializer, 
                many=True, 
                extra_field="group", 
                extra_field_value=instance.id
            )
        return instance

    def validate_permission(self, data):
        serializer = self.Meta.permission_serializer(data=data)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)
        
        return serializer.data