from django.utils.translation import gettext_lazy as _

class OrderVars:
    SELL_ORDER = "sale_order"
    PURCHASE_ORDER = "purchase_order"

    LOG_TYPES = [
        (SELL_ORDER, _("Sale order log")),
        (PURCHASE_ORDER, _("Purchase order log"))
    ]


class ExpenseVars:
    VAT_INKL = "inkl"
    VAT_EXKL = "excl"

    VAT_TYPES = [
        (VAT_INKL, _("Inkl.")),
        (VAT_EXKL, _("Excl."))
    ]
