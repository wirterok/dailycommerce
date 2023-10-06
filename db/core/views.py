from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.decorators import permission_classes, action, api_view
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.filters import OrderingFilter
from .serializers import (
    AuthAdminSerializer,
    TenantRegisterSerializer,
    SuperuserGroupSerializer,
    CreateSuperuserSerializer,
)
from db.helper_views import BaseAuthView
from db.db_utils import create_tenant_schema, run_command, set_tenant_for_request
from .models import Superuser, SuperuserGroup
from django.conf import settings
from db.local_settings import EmailTemplates
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from db.tokens import account_activation_token
from db.email import EmailManager
from db.filters import ConditionFilter, EdgeDateFilter, DateFilter, PermissionFilter
from django.conf import settings


@permission_classes([AllowAny])
class AuthorizeAdmin(BaseAuthView):
    serializer_class = AuthAdminSerializer


@permission_classes([AllowAny])
class RegisterAdmin(APIView):
    def post(self, request, *args, **kwargs):
        serializer = TenantRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=400, data=serializer.errors)

        data = serializer.validated_data
        company_name = data.pop("company_name")
        password = data.pop("password")

        tenant, tenant_created = create_tenant_schema(company_name)
        if not tenant_created:
            return Response(status=400, data={"msg": "This company already registered"})

        set_tenant_for_request(tenant.id)
        try:
            user = Superuser.objects.create(
                **data, is_active=False, is_superuser=True, is_confirmed=True, is_staff=True, tenant=tenant
            )
            user.set_password(password)
            user.save()
        except:
            tenant.delete()
            run_command(f"python {settings.BASE_DIR}/manage.py runscript update_db_conf")
            return Response(status=400, data={"msg": "This user already registered"})

        data = {
            "response": "Superuser succesfully registered",
            "username": user.username,
            "email": user.email,
            "company": tenant.company_name,
        }

        # email = EmailManager(request.tenant_id, EmailTemplates.CONFIRM, user)
        # url = (
        #     settings.HOST_URL
        #     + "/admin/confirm/"
        #     + urlsafe_base64_encode(force_bytes(user.id))
        #     + "/"
        #     + account_activation_token.make_token(user)
        # )
        # email.send(
        #     template_data={"name": user.username, "url": url, "storefront_url": EmailTemplates.EXTRA_SITE},
        #     to_user=[user.email],
        # )
        return Response(data)


class SuperuserGroupViewset(ModelViewSet):
    permission_classes = [IsAdminUser]
    filter_backends = [OrderingFilter, ConditionFilter, EdgeDateFilter]
    ordering_fields = [
        "name_EN",
        "name_DE",
        "description_EN",
        "description_DE",
        "discipline_EN",
        "discipline_DE",
        "created_at",
    ]
    model_class = SuperuserGroup
    queryset = model_class.objects.all()
    serializer_class = SuperuserGroupSerializer


class SuperUserViewset(ModelViewSet):
    permission_classes = [IsAdminUser]
    filter_backends = [OrderingFilter, ConditionFilter, EdgeDateFilter]
    ordering_fields = ["name", "email", "group"]
    model_class = Superuser
    queryset = model_class.objects.all()
    serializer_class = CreateSuperuserSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(tenant_id=self.request.tenant_id)


@api_view(["post"])
@permission_classes([AllowAny])
def collaborate(request, uid64, token):
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = Superuser.objects.get(pk=uid)

        password = request.data.get("password")
        if not password:
            raise ValueError
    except (TypeError, ValueError, OverflowError, Superuser.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_confirmed = True
        user.set_password(password)
        user.save()
        return Response("Account waa activated succesfully")
    else:
        return Response("Token is invalid", status=400)


@api_view(["post"])
@permission_classes([AllowAny])
def confirm(request, uid64, token):
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = Superuser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Superuser.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_confirmed = True
        user.save()
        return Response("Account waa activated succesfully")
    else:
        return Response("Token is invalid", status=400)


@api_view(["post"])
@permission_classes([AllowAny])
def reset_request(request):
    email = request.data.get("email")
    try:
        user = Superuser.objects.get(email=email)
        email = EmailManager(request.tenant_id, EmailTemplates.RESET, user)
        url = (
            settings.HOST_URL
            + "/account/reset_pass/"
            + urlsafe_base64_encode(force_bytes(user.id))
            + "/"
            + account_activation_token.make_token(user)
        )
        email.send(
            template_data={"name": user.username, "url": url, "storefront_url": EmailTemplates.EXTRA_SITE},
            to_user=[email],
        )
    except:
        return Response(data="No such user", status=400)


@api_view(["post"])
@permission_classes([AllowAny])
def reset_pass(request, uid64, token):
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = Superuser.objects.get(pk=uid)

        password = request.data.get("password")
        if not password:
            raise ValueError
    except (TypeError, ValueError, OverflowError, Superuser.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.set_password(password)
        user.save()
        return Response("Account waa activated succesfully")
    else:
        return Response("Token is invalid", status=400)


@api_view(["post"])
@permission_classes([AllowAny])
def reset(request, pk):
    user = Superuser.objects.get(pk=pk)
    old_password = request.data.get("old_password")
    password = request.data.get("new_password")
    if not user.check_password(old_password):
        return Response(status=200, data="Incorrect old password")

    user.set_password(password)
    user.save()
    return Response("Password was changed")
