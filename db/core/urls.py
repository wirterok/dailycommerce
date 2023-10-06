from django.urls import path, include
from rest_framework.routers import SimpleRouter

import db.core.views as admin_views

router = SimpleRouter()

router.register(r"groups", admin_views.SuperuserGroupViewset)
router.register(r"list", admin_views.SuperUserViewset)

urlpatterns = [
    path("register/", admin_views.RegisterAdmin.as_view()),
    path("authorize/", admin_views.AuthorizeAdmin.as_view()),
    path("confirm/<uid64>/<token>/", admin_views.confirm),
    path("collaborate/<uid64>/<token>/", admin_views.collaborate),
    path("reset_request/", admin_views.reset_request),
    path("reset_pass/<uid64>/<token>/", admin_views.reset_pass),
    path("reset/<pk>/", admin_views.reset),
    path("", include(router.urls)),
]