from django.utils.translation import gettext_lazy as _


class EmailTemplates:
    RESET = "reset_password"
    CONFIRM = "account_created"
    INVITE = "invitation"
    COLLABORATE = "collaboration"
    PURCHASE_INVOICE = "purchase_invoice"
    EXTRA_SITE = "sciencecore.com"

    TemplatesChoices = [
        (RESET, _("Reset your password")),
        (CONFIRM, _("Confirm your account")),
        (INVITE, _("Invitation to try our app")),
        (COLLABORATE, _("Invitation to collaborate under project")),
        (PURCHASE_INVOICE, _("Purchase invoice for order")),
    ]