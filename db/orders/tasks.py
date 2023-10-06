from db.db_utils import bulk_upsert, set_tenant_for_request
import pandas as pd
import numpy as np
from .models import PurchaseOrder, SalesOrder, ProductUnit
from db.local_settings.models import Languages
from db.account.models import Customer
from db.payment.models import Account, Payment
import datetime
import uuid
import json


def process_translate(df, fields, tenant_id):
    set_tenant_for_request(tenant_id)
    locales = Languages.objects.values_list("local", flat=True)
    lookups = []
    for lang in locales:
        locales += [f"{lang}_{f}" for f in fields]

    translate_df = df[df.columns[pd.Series(df.columns).str.insin(lookups)]]


def upload_user(df, prefix, tenant):
    set_tenant_for_request(tenant.id)
    fields = ["name", "street", "street_number", "zip", "city", "country", "phone", "email", "payment_account"]
    df = df.rename(columns={f"{prefix}{f}": f.replace(prefix, "") for f in fields})
    user_df = df[df.columns.intersection(fields)]
    user_df["username"] = user_df["email"]
    user_df["email"] = user_df["email"]
    user_df["is_superuser"] = False
    user_df["is_active"] = False
    user_df["is_staff"] = False
    user_df["is_confirmed"] = False
    user_df["date_joined"] = datetime.date.today()
    user_df["id"] = [uuid.uuid4().hex for _ in range(len(user_df))]
    user_df["tenant_id"] = tenant.id
    bulk_upsert(
        Customer,
        list(user_df.columns),
        [tuple(x) for x in user_df.values.tolist()],
        f"{tenant.db_name}_schema",
        conflict_on=["email"],
        returning=["id", "email"],
    )
    user_data = Customer.objects.filter(email__in=user_df["email"].tolist()).values_list("id", "email")
    result = pd.DataFrame(columns=[f"{prefix}id", f"{prefix}email"], data=user_data)
    return result


def get_payment_id(df, tenant):
    set_tenant_for_request(tenant.id)
    df = df.dropna()
    for data in df.reset_index().to_dict("records"):
        id_qs = Payment.objects.filter(id=data["payment"])
        if id_qs.exists():
            df.loc[[data["uid"]], ["payment"]] = id_qs.first().id
        else:
            df.loc[[data["uid"]], ["payment"]] = None
    return df.rename(columns={"payment": "payment_id"})


def get_account_id(df, tenant, type):
    set_tenant_for_request(tenant.id)
    df = df.dropna()
    df = df.rename(columns={f"{type}_account": "account"})
    df["account"] = df["account"].astype(str)
    for data in df.reset_index().to_dict("records"):
        id_qs = Account.objects.filter(account_number=data["account"])
        if id_qs.exists():
            df.loc[[data["uid"]], ["account"]] = id_qs.first().id
        else:
            df.loc[[data["uid"]], ["account"]] = None
    return df.rename(columns={"account": f"{type}_account_id"})


def update_serialized_order(df, tenant, type):
    set_tenant_for_request(tenant.id)
    data = df.to_dict("records")
    for order in data:
        serialized = order["serialized_products"].split(",")
        serialized = list(map(lambda x: x.strip(), serialized))
        if serialized:
            update = {f"{type}_order_id": order["id"]}
            ProductUnit.objects.filter(serial_num__in=serialized).update(**update)


def upload_purchase_order(request):
    tenant = request.tenant
    extra_fields = ["seller_id", "seller_email"]
    purchase_fields = [f.name for f in PurchaseOrder._meta.get_fields()] + extra_fields
    exclude_fields = ["serialized_products", "payment", "creditor_account"]

    file = request.FILES.get("file")
    df = (
        pd.read_csv(file, index_col=False, delimiter=";")
        .rename(columns={"createdAt": "created_at", "updatedAt": "updated_at", "price": "total_price"})
        .set_index("uid")
    )
    df["user_owner"] = request.user.id

    serialized = df[["serialized_products"]].reset_index()
    payments = df[["payment"]]
    payment_df = get_payment_id(payments, tenant)
    accounts = df[["creditor_account"]]
    account_df = get_account_id(accounts, tenant, "creditor")

    order_df = df[df.columns.intersection(purchase_fields).difference(exclude_fields)].reset_index()

    order_users = upload_user(df, "seller_", tenant)
    order_df = order_df.merge(order_users, on="seller_email", how="left")
    order_df = order_df.merge(payment_df, on="uid", how="left")
    order_df = order_df.merge(account_df, on="uid", how="left")

    order_df = order_df.drop(columns=["seller_email"])
    order_df["is_locked"] = order_df["is_locked"].fillna(False)
    order_df["order_date"] = order_df["order_date"].fillna(datetime.datetime.today())
    order_df = order_df.where(pd.notnull(order_df), None)
    order_df["enabled"] = False
    order_df["in_trash"] = False

    order_data = bulk_upsert(
        PurchaseOrder,
        list(order_df.columns),
        [tuple(x) for x in order_df.values.tolist()],
        f"{tenant.db_name}_schema",
        conflict_on=["uid"],
        do_update=True,
        returning=["id", "uid"],
    )

    # order_data = PurchaseOrder.objects.filter(uid__in=order_df["uid"].tolist()).values("id", "uid")
    order_data = [x.split(",") for x in order_data]
    created_order_df = pd.DataFrame(columns=["id", "uid"], data=order_data).merge(serialized, on="uid", how="left")
    update_serialized_order(created_order_df, tenant, "purchase")


def upload_sales_order(request):
    tenant = request.tenant
    extra_fields = ["buyer_id", "buyer_email"]
    purchase_fields = [f.name for f in SalesOrder._meta.get_fields()] + extra_fields
    exclude_fields = ["products", "payment", "debitor_account"]

    file = request.FILES.get("file")
    df = (
        pd.read_csv(file, index_col=False, delimiter=";")
        .rename(columns={"createdAt": "created_at", "updatedAt": "updated_at", "price": "total_price"})
        .set_index("uid")
    )
    df["user_owner"] = request.user.id

    serialized = df[["products"]].reset_index()
    payments = df[["payment"]]
    payment_df = get_payment_id(payments, tenant)
    accounts = df[["debitor_account"]]
    account_df = get_account_id(accounts, tenant, "debitor")

    order_df = df[df.columns.intersection(purchase_fields).difference(exclude_fields)].reset_index()

    order_users = upload_user(df, "buyer_", tenant)
    order_df = order_df.merge(order_users, on="buyer_email", how="left")
    order_df = order_df.merge(payment_df, on="uid", how="left")
    order_df = order_df.merge(account_df, on="uid", how="left")

    order_df = order_df.drop(columns=["buyer_email"])
    order_df["is_locked"] = order_df["is_locked"].fillna(False)
    order_df["invoice_date"] = order_df["invoice_date"].fillna(datetime.datetime.today())
    order_df = order_df.where(pd.notnull(order_df), None)
    order_df["enabled"] = False
    order_df["in_trash"] = False

    order_data = bulk_upsert(
        SalesOrder,
        list(order_df.columns),
        [tuple(x) for x in order_df.values.tolist()],
        f"{tenant.db_name}_schema",
        conflict_on=["uid"],
        do_update=True,
        returning=["id", "uid"],
    )

    order_data = [x.split(",") for x in order_data]
    created_order_df = (
        pd.DataFrame(columns=["id", "uid"], data=order_data)
        .merge(serialized, on="uid", how="left")
        .rename(columns={"products": "serialized_products"})
    )
    update_serialized_order(created_order_df, tenant, "sell")