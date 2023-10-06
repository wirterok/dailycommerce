from rest_framework import serializers
from .models import Superuser, SuperuserGroup, SuperuserPermission
from db.helper_serializers import GroupSerializer
from db.account.models import Customer
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from db.core import UserRole
from db.email import EmailManager
from db.local_settings import EmailTemplates
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from db.tokens import account_activation_token

from django.conf import settings

class AuthAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Superuser
        fields = ["username", "password"]
        extra_kwargs = {"username": {"validators": []}}

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")
        if username and password:
            users = self.Meta.model.objects.filter(Q(username=username) | Q(phone=username) | Q(email=username))
            if users.exists():
                user = users.first()
                valid = user.check_password(password)
                if not valid:
                    raise serializers.ValidationError("Password is not correct")
            else:
                raise serializers.ValidationError("User doesn`t exists")
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


class RegisterSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, style={"input_type": "password"}, write_only=True)
    username = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    phone = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    avatar = serializers.FileField(allow_empty_file=True)


class TenantRegisterSerializer(RegisterSerializer):
    company_name = serializers.CharField(max_length=128)


class SuperuserPermissionSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=SuperuserGroup.objects.all(), required=False)

    class Meta:
        model = SuperuserPermission
        fields = "__all__"


class SuperuserGroupSerializer(GroupSerializer):
    permissions = SuperuserPermissionSerializer(many=True, read_only=True)
    group_permissions = serializers.DictField(child=serializers.CharField(), write_only=True)

    class Meta:
        permission_serializer = SuperuserPermissionSerializer
        model = SuperuserGroup
        fields = "__all__"


class CreateSuperuserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=UserRole.RoleChoices, write_only=True)
    group = serializers.PrimaryKeyRelatedField(queryset=SuperuserGroup.objects.all(), required=False)
    tenant = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Superuser
        fields = [
            "id",
            "avatar",
            "name",
            "username",
            "email",
            "group",
            "role",
            "created_at",
            "lang",
            "is_active",
            "updated_at",
            "tenant",
        ]
        extra_kwargs = {"username": {"required": False}, "group": {"required": False, "allow_null": True}}
        read_only_fields = ["created_at", "updated_at", "lang", "is_active", "tenant"]

    def get_tenant(self, obj):
        return obj.tenant.company_name

    def save(self):
        self.validated_data["tenant_id"] = self.context["request"].tenant_id
        if not self.validated_data.get("username"):
            self.validated_data["username"] = self.validated_data["email"]

        if self.validated_data.pop("role") == UserRole.ADMIN:
            self.validated_data["is_staff"] = True
            try:
                instance = super().save()
            except Exception as e:
                raise ValidationError(e)
            email = EmailManager(self.context["request"].tenant_id, EmailTemplates.COLLABORATE, instance)
            email.send(
                template_data={
                    "name": self.context["request"].user.username,
                    "url": settings.HOST_URL + "/admin/collaborate/",
                    "uid": urlsafe_base64_encode(force_bytes(instance.id)),
                    "token": account_activation_token.make_token(instance),
                    "storefront_url": EmailTemplates.EXTRA_SITE,
                },
                to_user=[instance.email],
            )
        else:
            try:
                instance = Customer.objects.create(**self.validated_data)
            except Exception as e:
                raise ValidationError(e)
            email = EmailManager(self.context["request"].tenant_id, EmailTemplates.INVITE, instance)
            email.send(
                template_data={
                    "tenant": self.context["request"].tenant,
                    "name": instance.username,
                    "url": settings.HOST_URL + "/account/invite",
                    "uid": urlsafe_base64_encode(force_bytes(instance.id)),
                    "token": account_activation_token.make_token(instance),
                    "storefront_url": EmailTemplates.EXTRA_SITE,
                },
                to_user=[instance.email],
            )
        return instance

    def to_representation(self, obj):
        data = super().to_representation(obj)
        if isinstance(obj, self.Meta.model):
            data["role"] = "Admin"
        else:
            data["role"] = "User"
        return data
