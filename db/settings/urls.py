from rest_framework.routers import SimpleRouter
from db.settings import views as settings_views
from django.urls import path, include

company_router = SimpleRouter()
shop_router = SimpleRouter()

company_router.register(r"company", settings_views.CompanySettingsViewset)
company_router.register(r"smtp", settings_views.SMTPViewset)
company_router.register(r"orderpurchases", settings_views.PurchaseOrderViewset)
company_router.register(r"salesorders", settings_views.SalesOrderViewset)
company_router.register(r"image", settings_views.ImageSettingViewset)
company_router.register(r"uid", settings_views.UIDViewset)


shop_router.register(r"shop", settings_views.ShopSettingViewset)
shop_router.register(r"styling", settings_views.ShopStylingViewset)
shop_router.register(r"newsletter", settings_views.ShopNewsletterViewset)
shop_router.register(r"header", settings_views.HeaderViewset)

urlpatterns = [path("", include(company_router.urls)), path("countries", settings_views.get_countries)]
