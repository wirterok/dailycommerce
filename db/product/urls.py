from rest_framework.routers import SimpleRouter
from . import views as product_view

router = SimpleRouter()

router.register(r"category", product_view.CategoryViewSet)
router.register(r"attribute", product_view.AttributeViewSet)
router.register(r"tags", product_view.TagViewSet)
router.register(r"products", product_view.ProductViewSet)
router.register(r"service", product_view.ProductServiceViewSet)