from rest_framework.routers import SimpleRouter
from db.local_settings import views

router = SimpleRouter()
shop_router = SimpleRouter()

router.register(r"languages", views.LanguageViewSet)
router.register(r"tax", views.TaxViewSet)
router.register(r"templates", views.EmailTemplateViewset)
router.register(r"dhl", views.DeliveryViewset)

shop_router.register(r"custompages", views.CustomPagesViewset)
shop_router.register(r"customelements", views.CustomElementsViewset)
