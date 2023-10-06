from db.product.models import File
from db.core.models import Token
from db.serializers import FileSerializer
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .managers import DashnoardManager
from .permissions import CustomPermission
from django.http import HttpResponse


class FileViewSet(GenericViewSet, CreateModelMixin, ListModelMixin):
    model_class = File
    queryset = model_class.objects.all()
    serializer_class = FileSerializer


class DashboardView(APIView):
    permission_classes = [CustomPermission, IsAdminUser]

    def get(self, request, *args, **kwargs):
        data = DashnoardManager(request).result()
        return Response(status=200, data=data)


def introspect_view(request):
    token = request.META.get("HTTP_AUTHORIZATION")
    if not token:
        return HttpResponse(status=401, content="Unauthorized")
    try:
        token = token.split(" ")[1]
        token = Token.objects.get(key=token)
        return HttpResponse(status=200, content="Ok")
    except:
        return HttpResponse(status=401, content="Unauthorized")
