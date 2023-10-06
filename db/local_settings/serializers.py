from rest_framework.serializers import ModelSerializer
from db.local_settings import models as settings_models


class TaxSerializer(ModelSerializer):
    class Meta:
        model = settings_models.Tax
        fields = "__all__"


class LanguageSerializer(ModelSerializer):
    class Meta:
        model = settings_models.Languages
        fields = "__all__"


class EmailTemplateSerializer(ModelSerializer):
    class Meta:
        model = settings_models.EmailTemplate
        fields = "__all__"
        validators = []


class CustomPagesSerializer(ModelSerializer):
    class Meta:
        model = settings_models.CustomPages
        fields = "__all__"
        validators = []


class CustomElementsSerializer(ModelSerializer):
    class Meta:
        model = settings_models.CustomElements
        fields = "__all__"
        validators = []


class DeliverySettingsSerializer(ModelSerializer):
    class Meta:
        model = settings_models.DeliverySettings
        fields = "__all__"
        extra_kwargs = {
            "type": {"validators": []}
        }
