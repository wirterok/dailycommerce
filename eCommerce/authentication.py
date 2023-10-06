from rest_framework.authentication import TokenAuthentication
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from db.core.models import Token, Superuser
from db.account.models import Customer


class ExtendedTokenAuthentication(TokenAuthentication):
    model = Token

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related("tenant").get(key=key)
        except model.DoesNotExist:
            raise exceptions.NotAuthenticated(_("Invalid token."))

        user_qs = Superuser.objects.filter(id=token.user)

        if user_qs.exists():
            user = user_qs.first()
        else:
            user_qs = Customer.objects.filter(id=token.user)
            if user_qs.exists():
                user = user_qs.first()
            else:
                raise exceptions.AuthenticationFailed(_("User does not exists"))

        if not user.is_active:
            raise exceptions.AuthenticationFailed(_("User inactive or deleted."))

        return (user, token)
