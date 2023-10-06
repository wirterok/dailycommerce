from django.db import models
from db.local_settings import EmailTemplates

# Create your models here.

class Languages(models.Model):
    is_primary = models.BooleanField(default=False)
    locale = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=24)


class EmailTemplate(models.Model):
    lang = models.CharField(max_length=12)
    template = models.CharField(max_length=64, choices=EmailTemplates.TemplatesChoices)
    html = models.TextField()

    class Meta:
        unique_together = ["lang", "template"]


class Tax(models.Model):
    tax_title = models.CharField(max_length=128)
    tax_description = models.TextField(null=True)
    tax_rate = models.DecimalField(max_digits=7, decimal_places=4, default=0, null=True)


class CustomPages(models.Model):
    lang = models.CharField(max_length=12)
    page_category = models.CharField(max_length=128, null=True)
    page_inner = models.TextField(null=True)
    page_name = models.CharField(max_length=64)
    page_title = models.CharField(max_length=254, null=True) 

    class Meta:
        unique_together = ["lang", "page_name"]


class CustomElements(models.Model):
    lang = models.CharField(max_length=12)
    element_content = models.TextField(null=True)
    element_location = models.CharField(max_length=128)
    element_title = models.CharField(max_length=128, null=True)

    class Meta:
        unique_together = ["lang", "element_location"]
        

class DeliverySettings(models.Model):
    app_name = models.CharField(max_length=64, null=True, blank=True)
    password = models.CharField(max_length=64, null=True, blank=True)
    signature = models.CharField(max_length=128, null=True, blank=True)
    type = models.CharField(max_length=24, unique=True)
    acc_number = models.CharField(max_length=64, null=True, blank=True)
    user = models.CharField(max_length=64, null=True, blank=True)
    user_password = models.CharField(max_length=64, null=True, blank=True)
    username = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return self.type