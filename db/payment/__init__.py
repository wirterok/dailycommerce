from django.utils.translation import gettext_lazy as _

class PaymentChoices:
    CUSTOM = "custom"
    PRIVATE = "private"
    FINANCES = "finances"
    OFFICE = "office"
    SERVICES = "services"
    VECHICLE = "vechicle"
    MACHINE = "machine"
    MATERIAL = "material"
    HR = "hr"
    OCCUPANCY = "occupancy"
    TRAVEL = "travel"
    MISCELLANEOUS = "miscellaneous"
    INSURANCE = "insurance"
    ADVERTASING = "advertasing"
    LIABILITIES = "liabilities"
    OBLIGATION = "obligation"
    TAXES = "taxes"
    MISCELLANEOUS_EARNINGS = "miscellaneous_earnings"

    PURCHASE_ORDER = "purchase_order"
    SALE_ORDER = "selling_order"

    DEFAULT_FOR = [
        (PURCHASE_ORDER, _("Purchase order")),
        (SALE_ORDER, _("Selling order"))
    ]