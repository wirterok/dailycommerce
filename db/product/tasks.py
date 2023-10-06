from .models import ProductData, Product, ProductCategory
from db.db_utils import set_tenant_for_request, bulk_upsert
import pandas as pd


def get_category_id(df, tenant):
    set_tenant_for_request(tenant.id)
    df = df.dropna()
    for data in df.reset_index().to_dict("records"):
        id_qs = ProductCategory.objects.filter(uid=data["category"])
        if id_qs.exists():
            df.loc[[data["sku"]], ["category"]] = id_qs.first().id
        else:
            df.loc[[data["sku"]], ["category"]] = None
    return df.rename(columns={"category": "category_id"})


def upload_product_csv(request):
    tenant = request.tenant
    product_data_fields = [f.name for f in ProductData._meta.get_fields()]

    product_fields = [f.name for f in Product._meta.get_fields()]
    exclude_product_fields = ["exp", "attributes", "alternate_images", "translations", "category"]
    exclude_product_data_fields = ["translations", "created_at", "updated_at"]

    file = request.FILES.get("file")
    df = (
        pd.read_csv(file, index_col=False, delimiter=",")
        .rename(columns={"createdAt": "created_at", "updatedAt": "updated_at", "product_group": "category"})
        .set_index("sku")
    )
    df = df.where(pd.notnull(df), None)
    df["user_owner"] = request.user.id
    
    category_df = get_category_id(df[["category"]], tenant)
    product_df = (
        df[df.columns.intersection(product_fields).difference(exclude_product_fields)]
        .reset_index()
        .merge(category_df, on="sku", how="left")
    )
    product_df["serialized"] = False
    product_df["in_trash"] = False

    product_data = bulk_upsert(
        Product,
        list(product_df.columns),
        [tuple(x) for x in product_df.values.tolist()],
        f"{tenant.db_name}_schema",
        conflict_on=["sku"],
        do_update=True,
        returning=["id", "sku"],
    )
    product_data = [x.split(",") for x in product_data]
    new_product_df = pd.DataFrame(columns=["product_id", "sku"], data=product_data)
    product_data_df = (
        df[df.columns.intersection(product_data_fields)]
        .dropna(how="all")
        .reset_index()
        .merge(new_product_df, on="sku", how="inner")
        .drop(columns=["sku"])
    )

    bulk_upsert(
        ProductData,
        list(product_data_df.columns),
        [tuple(x) for x in product_data_df.values.tolist()],
        f"{tenant.db_name}_schema",
        conflict_on=["product_id"],
        do_update=True,
        returning=["id"],
    )
