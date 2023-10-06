from django.shortcuts import render
from db.helper_views import BaseSettingsView
from db.local_settings import models as settings_models
from db.local_settings import serializers as settings_serializers
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet
# Create your views here.


class LanguageViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    model_class = settings_models.Languages
    queryset = model_class.objects.all()
    serializer_class = settings_serializers.LanguageSerializer


class TaxViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    model_class = settings_models.Tax
    queryset = model_class.objects.all()
    serializer_class = settings_serializers.TaxSerializer


class EmailTemplateViewset(BaseSettingsView):
    model_class = settings_models.EmailTemplate
    queryset = model_class.objects.all()
    serializer_class = settings_serializers.EmailTemplateSerializer

    def get_filtered_queryset(self):
        qs = super().get_filtered_queryset()
        lang = self.request.data.get("lang")
        template = self.request.data.get("template")
        return qs.filter(lang=lang, template=template)


class CustomPagesViewset(BaseSettingsView):
    model_class = settings_models.CustomPages
    queryset = model_class.objects.all()
    serializer_class = settings_serializers.CustomPagesSerializer

    def get_filtered_queryset(self):
        qs = super().get_filtered_queryset()
        lang = self.request.data.get("lang")
        page_name = self.request.data.get("page_name")
        return qs.filter(lang=lang, page_name=page_name)


class CustomElementsViewset(BaseSettingsView):
    model_class = settings_models.CustomElements
    queryset = model_class.objects.all()
    serializer_class = settings_serializers.CustomElementsSerializer

    def get_filtered_queryset(self):
        qs = super().get_filtered_queryset()
        lang = self.request.data.get("lang")
        location = self.request.data.get("element_location")
        return qs.filter(lang=lang, element_location=location)


class DeliveryViewset(BaseSettingsView):
    model_class = settings_models.DeliverySettings
    queryset = model_class.objects.all()
    serializer_class = settings_serializers.DeliverySettingsSerializer
    
    def get_filtered_queryset(self):
        qs = super().get_filtered_queryset()
        type = self.request.data.get("type")
        return qs.filter(type=type)