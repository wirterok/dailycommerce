from django.db import models
from db.core.models import Tenant
# Create your models here.


class CompanySettings(models.Model):
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, null=True, blank=True)
    street = models.CharField(max_length=128, null=True, blank=True)
    zip = models.CharField(max_length=24, null=True, blank=True)
    city = models.CharField(max_length=64, null=True, blank=True)
    country = models.CharField(max_length=64, null=True, blank=True)
    court = models.CharField(max_length=128, null=True, blank=True)
    ceo = models.CharField(max_length=128, null=True, blank=True)
    tax = models.CharField(max_length=64, null=True, blank=True)
    vat = models.CharField(max_length=64, null=True, blank=True)
    bank = models.CharField(max_length=64, null=True, blank=True)
    owner = models.CharField(max_length=64, null=True, blank=True)
    iban = models.CharField(max_length=64, null=True, blank=True)
    bic = models.CharField(max_length=64, null=True, blank=True)
    slogan = models.CharField(max_length=64, null=True, blank=True)
    logo = models.ImageField(upload_to="company_logo", null=True, blank=True)

    def __str__(self):
        return self.name


class SMTP(models.Model):
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE)
    host = models.CharField(max_length=32, null=True, blank=True)
    port = models.CharField(max_length=16, null=True, blank=True)
    sender_name = models.CharField(max_length=128, null=True, blank=True)
    user = models.CharField(max_length=128, null=True, blank=True)
    password = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return self.host + ":" + self.port


class PurchaseOrderSettings(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    lang = models.CharField(max_length=24)

    class Meta:
        unique_together = ["tenant_id", "lang"]


class SalesOrderSettings(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    lang = models.CharField(max_length=24)
    collections = models.JSONField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    tags = models.JSONField(null=True, blank=True)
    header = models.CharField(max_length=128, null=True, blank=True)
    header_bottom = models.CharField(max_length=128, null=True, blank=True)
    type = models.CharField(max_length=64, null=True, blank=True)
    template_name = models.CharField(max_length=128, null=True, blank=True)
    template_signature = models.CharField(max_length=128, null=True, blank=True)
    template_suffix = models.CharField(max_length=64, null=True, blank=True)
    template_text = models.TextField(null=True, blank=True)
    
    class Meta:
        unique_together = ["tenant_id", "lang"]


class ImageSettings(models.Model):
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE)
    icon_width = models.IntegerField()
    preview_width = models.IntegerField()


class ShopSettings(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    lang = models.CharField(max_length=24)
    breadcrumbs_on = models.BooleanField(default=False)
    locale = models.CharField(max_length=128, null=True, blank=True)
    shop_hotline = models.CharField(max_length=128, null=True, blank=True)
    shop_tagline = models.CharField(max_length=128, null=True, blank=True)
    shop_title = models.CharField(max_length=128, null=True, blank=True)
    shop_url = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        unique_together = ["tenant_id", "lang"]


class ShopStyling(models.Model):
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to="shop", null=True, blank=True)
    icon = models.ImageField(upload_to="shop", null=True, blank=True)
    skin_type = models.CharField(max_length=24, null=True, blank=True)
    type = models.CharField(max_length=128, null=True, blank=True)
    lazy_load = models.BooleanField(default=False)
    preloades = models.BooleanField(default=False)
    custom_css = models.CharField(max_length=64, null=True, blank=True)
    color1 = models.CharField(max_length=8, null=True, blank=True)
    color2 = models.CharField(max_length=8, null=True, blank=True)
    color3 = models.CharField(max_length=8, null=True, blank=True)


class ShopNewsletter(models.Model):
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE)
    lang = models.CharField(max_length=24)
    type = models.CharField(max_length=128, null=True, blank=True)
    target_url = models.CharField(max_length=128, null=True, blank=True)
    popup_text = models.CharField(max_length=256, null=True, blank=True)
    button_text = models.CharField(max_length=256, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    popup_image = models.ImageField(upload_to="shop", null=True, blank=True)

    class Meta:
        unique_together = ["tenant_id", "lang"]


class UID(models.Model):
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE)
    type = models.CharField(max_length=64, default="uidSettings", null=True, blank=True)
    expenses = models.JSONField(null=True, blank=True)
    help_desk_tickets = models.JSONField(null=True, blank=True)
    inventory = models.JSONField(null=True, blank=True)
    payments = models.JSONField(null=True, blank=True)
    purchase_order = models.JSONField(null=True, blank=True)
    sales_order = models.JSONField(null=True, blank=True)


class HeaderSettings(models.Model):
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE)
    type = models.CharField(max_length=64, default="headerSettings", null=True, blank=True)
    layout = models.CharField(max_length=64, null=True, blank=True)
    elements = models.JSONField(null=True, blank=True)
    is_sticky = models.BooleanField(default=False, blank=True)
