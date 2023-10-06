from django.urls import path, include
import db.account.views as account_views


urlpatterns = [
    path("register/", account_views.RegisterUser.as_view()),
    path("authorize/", account_views.AuthorizeView.as_view()),
    path("confirm/<tenant_id>/<uid64>/<token>/", account_views.confirm),
    path("invite/<tenant_id>/<uid64>/<token>/", account_views.collaborate),
    path("reset_request/", account_views.reset_request),
    path("reset_pass/<tenant_id>/<uid64>/<token>/", account_views.reset_pass),
    path("reset/<pk>/", account_views.reset),
]