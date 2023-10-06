from django.shortcuts import render
import json

# Create your views here.
from rest_framework import viewsets
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from db.account.models import Translation, Customer
from db.core.models import Token, Superuser
from db.helper_serializers import TranslationSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAdminUser

from db.local_settings import EmailTemplates
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from db.tokens import account_activation_token
from db.email import EmailManager
from django.conf import settings


class DefaultPagination(PageNumberPagination):
    page_size = 200
    page_size_query_param = "perPage"
    max_page_size = 1000


class ExtendViewset(viewsets.ViewSet):
    @property
    def client(self):
        return self.request.client


class BaseModelsViewset(viewsets.ModelViewSet):
    pagination_class = DefaultPagination

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.prefetch_related("translations")

    @action(methods=["post"], detail=True)
    def set_translation(self, request, pk=None):
        obj = self.get_object()
        serializer = TranslationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(status=300, data={"message: Passed data is not valid"})

        obj.translations.update_or_create(**serializer.data)
        return Response(status=200, data={"message": "Translation created"})

    @action(methods=["post"], detail=True)
    def delete_translation(self, request, pk=None):
        obj = self.get_object()
        translation_id = request.query_params.get("translation_id", None)
        try:
            translation = Translation.objects.get(id=translation_id)
            translation.delete()
            return Response(status=200, data={"message": "Translation was delete succesfully"})
        except:
            return Response(status=404, data={"message": "Translation not found"})


class CustomQuerysetViewSet(viewsets.ModelViewSet):
    pagination_class = DefaultPagination

    def get_list(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CustomTrashViewSet(BaseModelsViewset):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(in_trash=False)
        return qs

    @action(methods=["post"], detail=False)
    def put_to_trash(self, request):
        ids = request.data.get("id", [])
        ids = json.loads(ids)
        qs = super().get_queryset()
        qs.filter(id__in=ids).update(in_trash=True)
        return Response(data={"msg": "Changed"})


class BaseAuthView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        if not user.is_confirmed:
            if isinstance(user, Superuser):
                url = (
                    settings.HOST_URL + "/admin/confirm/" + 
                    urlsafe_base64_encode(force_bytes(user.id)) + "/" + 
                    account_activation_token.make_token(user)
                )
            else:
                url = (
                    settings.HOST_URL + "/account/confirm/" + str(request.tenant.id) + "/" +
                    urlsafe_base64_encode(force_bytes(user.id)) + "/" + 
                    account_activation_token.make_token(user)
                )

            email = EmailManager(user.tenant_id, EmailTemplates.CONFIRM, user)
            email.send(
                template_data={
                    "name": user.username,
                    "url": url,
                    "storefront_url": EmailTemplates.EXTRA_SITE
                },
                to_user=[user.email]
            )
            return Response(
                status=400,
                data="Account with this email is created already, but not confirmed yet. Confirmation letter was sent!",
            )

        user_tokens = Token.objects.filter(user=user.id, tenant_id=user.tenant_id)
        if user_tokens.exists():
            user_tokens.first().delete()
        token = Token.objects.create(user=user.id, tenant_id=user.tenant_id)
        user.is_active = True
        user.save()
        respose = {
            "id": user.id,
            "username": user.username,
            "token": token.key,
        }
        if isinstance(user, Superuser):
            respose.update({"tenant_id": user.tenant_id})
        return Response(status=200, data=respose)


class BaseSettingsView(viewsets.GenericViewSet, CreateModelMixin, ListModelMixin):
    permission_classes = [IsAdminUser]

    def get_filtered_queryset(self):
        return self.get_queryset()

    def create(self, request, *args, **kwargs):
        qs = self.get_filtered_queryset()
        data = dict(request.data)
        data.update({"tenant_id": self.request.tenant_id})
        if qs.exists():
            instance = qs.first()
            serializer = self.get_serializer(data=data)
            if not serializer.is_valid():
                return Response(status=400, data=serializer.errors)

            serializer.update(instance=instance, validated_data=serializer.validated_data)
            return Response(status=200, data=serializer.data)

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=400, data=serializer.errors)
        self.perform_create(serializer)
        return Response(status=200, data=serializer.data)