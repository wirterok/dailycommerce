from db.settings import models as settings_models
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField


class BaseSettingSerializer(ModelSerializer):
    tenant = PrimaryKeyRelatedField(read_only=True)

    def save(self):
        user = self.context["request"].user
        self.validated_data["tenant_id"] = user.tenant.id
        return super().save()
        
        
class CompanySettingSerializer(BaseSettingSerializer):
    class Meta:
        model = settings_models.CompanySettings
        fields = "__all__"
        read_only_fields = ["tenant"]


class SMTPSerializer(BaseSettingSerializer):
    class Meta:
        model = settings_models.SMTP
        fields = "__all__"

    def to_representation(self, obj):
        data = super().to_representation(obj)
        data["password"] = None
        return data


class PurchaseOrderSettingsSerializer(BaseSettingSerializer):
    class Meta:
        model = settings_models.PurchaseOrderSettings
        fields = "__all__"


class SalesOrderSettingsSerializer(BaseSettingSerializer):
    class Meta:
        model = settings_models.SalesOrderSettings
        fields = "__all__"


class ImageSettingsSerializer(BaseSettingSerializer):
    class Meta:
        model = settings_models.ImageSettings
        fields = "__all__"


class ShopSettingsSerializer(BaseSettingSerializer):
    class Meta:
        model = settings_models.ShopSettings
        fields = "__all__"


class ShopStylingSerializer(BaseSettingSerializer):
    class Meta:
        model = settings_models.ShopStyling
        fields = "__all__"


class ShopNewsletterSerializer(BaseSettingSerializer):
    class Meta:
        model = settings_models.ShopNewsletter
        fields = "__all__"


class UIDSerializer(BaseSettingSerializer):
    class Meta:
        model = settings_models.UID
        fields = "__all__"


class HeaderSerializer(BaseSettingSerializer):
    class Meta:
        model = settings_models.HeaderSettings
        fields = "__all__"