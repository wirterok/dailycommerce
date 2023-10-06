from rest_framework.routers import SimpleRouter
from . import views as payment_view

router = SimpleRouter()

router.register(r"payment", payment_view.PaymentViewSet)
router.register(r"accounts", payment_view.AccountViewSet)
router.register(r"paymentaccounts", payment_view.PaymentAccountViewSet)