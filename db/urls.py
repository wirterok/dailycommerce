from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .product.urls import router as product_router
from .orders.urls import router as order_router
from .warehouse.urls import router as warehouse_router
from .payment.urls import router as payment_router
from .service.urls import router as service_router
from .settings import urls as settings_urls
from .local_settings import urls as local_settings_urls
from .views import FileViewSet, DashboardView, introspect_view


current_router = SimpleRouter()
current_router.register(r"upload", FileViewSet)

urlpatterns = [
    path("dashboard/", DashboardView.as_view()),
    path("introspect/", introspect_view),
    path("product/", include(product_router.urls)),
    path("order/", include(order_router.urls)),
    path("account/", include("db.account.urls")),
    path("admin/", include("db.core.urls")),
    path("warehouse/", include(warehouse_router.urls)),
    path("payment/", include(payment_router.urls)),
    path("service/", include(service_router.urls)),
    path("settings/", include("db.settings.urls")),
    path("shopsettings/", include(settings_urls.shop_router.urls)),
    path("settings/", include(local_settings_urls.router.urls)),
    path("shopsettings/", include(local_settings_urls.shop_router.urls)),
    path("file/", include(current_router.urls)),
]