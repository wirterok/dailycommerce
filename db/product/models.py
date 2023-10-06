from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from db.account.models import Translation
from db.helper_models import BaseModel
from db.payment.models import Account
# Create your models here.


class File(BaseModel):
    file = models.FileField(upload_to="files/")


class ProductCategory(MPTTModel):
    translations = models.ManyToManyField(Translation, related_name="categories", blank=True)

    key = models.CharField(max_length=125, null=True, blank=True)
    uid = models.CharField(max_length=125, null=True, blank=True, unique=True)
    avatar = models.ImageField(upload_to="category-images")
    name = models.CharField(max_length=256)
    description = models.TextField()
    parent = TreeForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    user_owner = models.CharField(max_length=128)
    in_trash = models.BooleanField(null=True, default=False)

    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.uid} | {self.name}" 
    
    def save(self, force_insert=False, force_update=False, request=None, *args, **kwargs):
        if request:
            self.user_owner = request.user.id

        super().save(force_insert, force_update, *args, **kwargs)
        

class ProductAttribute(BaseModel):
    user_owner = models.CharField(max_length=128)
    translations = models.ManyToManyField(Translation, related_name="attributes")
    
    name = models.CharField(max_length=128)
    description = models.TextField()
    terms = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, request=None, *args, **kwargs):
        if request:
            self.user_owner = request.user.id

        super().save(force_insert, force_update, *args, **kwargs)


class ProductTag(models.Model):
    user_owner = models.CharField(max_length=128)
    translations = models.ManyToManyField(Translation, related_name="tags")
    
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def save(self, force_insert=False, force_update=False, request=None, *args, **kwargs):
        if request:
            self.user_owner = request.user.id

        super().save(force_insert, force_update, *args, **kwargs)


class Product(BaseModel):
    attributes = models.JSONField(null=True, blank=True)
    category = models.ForeignKey(ProductCategory, related_name="products", on_delete=models.SET_NULL, null=True)
    translations = models.ManyToManyField(Translation, related_name="products")
    tags = models.ManyToManyField(ProductTag, related_name="products", blank=True)
    alternate_images = models.ManyToManyField(File, related_name="products", blank=True)
    user_owner = models.CharField(max_length=128)

    purchase_price = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    title = models.CharField(max_length=125)
    description = models.TextField(null=True)
    condition = models.CharField(max_length=128, null=True)
    type = models.CharField(max_length=125, null=True)
    sku = models.CharField(max_length=125, unique=True)
    marketplace_sku = models.CharField(max_length=125, null=True)
    serialized = models.BooleanField(default=False)
    in_trash = models.BooleanField(null=True, default=False)

    def __str__(self):
        return f"{self.sku} | {self.title}"
    
    def save(self, force_insert=False, force_update=False, request=None, *args, **kwargs):
        if request:
            self.user_owner = request.user.id

        super().save(force_insert, force_update, *args, **kwargs)


class QualityData(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="exp")
    quality_text = models.CharField(max_length=128)
    quality_description = models.TextField(blank=True, null=True)
    files = models.ManyToManyField(File, related_name="quality", blank=True)

    def __str__(self):
        return self.condition
    
    @property
    def images_list(self):
        images_qs = self.images.all() 
        images_list = [default_storage.url(str(obj.image)) for obj in images_qs]
        return images_list

    class Meta:
        unique_together = ["product_id", "quality_text"]


class ProductData(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="extra_data")
    brand = models.CharField(max_length=125, null=True, blank=True)
    designer = models.CharField(max_length=125, null=True, blank=True)
    manufacturer = models.CharField(max_length=125, null=True, blank=True)
    bullet_point = models.CharField(max_length=10, null=True, blank=True)
    merchant_catalog_number = models.CharField(max_length=25, null=True, blank=True)
    serial_number_req = models.CharField(max_length=125, null=True, blank=True)
    legal_disclamer = models.TextField(null=True, blank=True)
    mfr_part_number = models.CharField(max_length=25, null=True, blank=True)
    search_terms = models.TextField(null=True, blank=True)
    platinum_keywords = models.TextField(null=True, blank=True)
    browse_node = models.CharField(max_length=126, null=True, blank=True)
    memorabilia = models.CharField(max_length=126, null=True, blank=True)
    autographed = models.BooleanField(default=False, null=True, blank=True)
    other_item_attributes = models.CharField(max_length=256, null=True, blank=True)
    target_audience = models.CharField(max_length=125, null=True, blank=True)
    subject_content = models.TextField(null=True, blank=True)
    tsd_age_warning = models.CharField(max_length=24, null=True, blank=True)
    tsd_warning = models.CharField(max_length=128, null=True, blank=True)	
    tsd_language = models.CharField(max_length=24, null=True, blank=True)
    product_data = models.CharField(max_length=512, null=True, blank=True)    
    variation = models.CharField(max_length=128, null=True, blank=True)
    item_dimensions = models.CharField(max_length=24, null=True, blank=True)
    package_dimensions = models.CharField(max_length=24, null=True, blank=True)
    package_weight = models.CharField(max_length=24, null=True, blank=True)


class ProductService(BaseModel):
    name = models.CharField(max_length=128)
    description = models.TextField()
    purchase_price = models.DecimalField(max_digits=7, decimal_places=2)
    price_gross = models.DecimalField(max_digits=7, decimal_places=2)
    price_net = models.DecimalField(max_digits=7, decimal_places=2)
    price_tax = models.DecimalField(max_digits=7, decimal_places=2)
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    default_import = models.CharField(max_length=256)
    user_owner = models.CharField(max_length=128)

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, request=None, *args, **kwargs):
        if request:
            self.user_owner = request.user.id

        super().save(force_insert, force_update, *args, **kwargs)
    
