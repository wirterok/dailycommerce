from rest_framework.routers import SimpleRouter
from . import views as order_view

router = SimpleRouter()

router.register(r"serialized", order_view.SerializedViewSet)
router.register(r"orderpurchased", order_view.PurchaseViewSet)
router.register(r"salesorder", order_view.SalesOrderViewSet)
router.register(r"invoice", order_view.InvoiceViewSet)