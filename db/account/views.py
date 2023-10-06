from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.decorators import permission_classes, action, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ViewSet

from .serializers import CustomerSerializer, AuthCustomerSerializer, CustomerRegisterSerializer
from db.core.models import Tenant, Token
from db.helper_views import BaseAuthView
from .models import Customer

from db.local_settings import EmailTemplates
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from db.tokens import account_activation_token
from db.db_utils import set_tenant_for_request
from db.email import EmailManager
from django.conf import settings


@permission_classes([AllowAny])
class AuthorizeView(BaseAuthView):
    serializer_class = AuthCustomerSerializer


@permission_classes([AllowAny])
class RegisterUser(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CustomerRegisterSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            user = serializer.save(request=request)
            data = {
                "response": "User succesfully registered",
                "username": user.username,
                "email": user.email,
                "token": Token.objects.get(user=user.id, tenant_id=user.tenant_id).key,
            }
        else:
            return Response(serializer.errors, status=400)

        # email = EmailManager(request.tenant_id, EmailTemplates.CONFIRM, user)
        # url = (
        #     settings.HOST_URL
        #     + "/account/confirm/"
        #     + f"{request.tenant_id}/"
        #     + urlsafe_base64_encode(force_bytes(user.id))
        #     + "/"
        #     + account_activation_token.make_token(user)
        # )
        # email.send(
        #     template_data={"name": user.username, "url": url, "storefront_url": EmailTemplates.EXTRA_SITE},
        #     to_user=[user.email],
        # )

        return Response(data)


@api_view(["post"])
@permission_classes([AllowAny])
def collaborate(request, tenant_id, uid64, token):
    set_tenant_for_request(tenant_id)
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = Customer.objects.get(pk=uid)

        password = request.data.get("password")
        if not password:
            raise ValueError
    except (TypeError, ValueError, OverflowError, Customer.DoesNotExist):
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
def confirm(request, tenant_id, uid64, token):
    set_tenant_for_request(tenant_id)
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = Customer.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Customer.DoesNotExist):
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
        user = Customer.objects.get(email=email)
        email = EmailManager(request.tenant_id, EmailTemplates.RESET, user)
        url = (
            settings.HOST_URL
            + "/account/reset_pass/"
            + str(request.tenant_id)
            + "/"
            + urlsafe_base64_encode(force_bytes(user.id))
            + "/"
            + account_activation_token.make_token(user)
        )
        email.send(
            template_data={"name": user.username, "url": url, "storefront_url": EmailTemplates.EXTRA_SITE},
            to_user=[user.email],
        )
        return Response(data="Reset url was sent")
    except:
        return Response(data="No such user", status=400)


@api_view(["post"])
@permission_classes([AllowAny])
def reset_pass(request, tenant_id, uid64, token):
    set_tenant_for_request(tenant_id)
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = Customer.objects.get(pk=uid)

        password = request.data.get("password")
        if not password:
            raise ValueError
    except (TypeError, ValueError, OverflowError, Customer.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.set_password(password)
        user.save()
        return Response("Password was changed succesfully")
    else:
        return Response("Token is invalid", status=400)


@api_view(["post"])
@permission_classes([AllowAny])
def reset(request, pk):
    user = Customer.objects.get(pk=pk)
    old_password = request.data.get("old_password")
    password = request.data.get("new_password")
    if not user.check_password(old_password):
        return Response(status=200, data="Incorrect old password")

    user.set_password(password)
    user.save()
    return Response("Password was changed")