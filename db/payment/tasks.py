import pandas as pd
from .models import Payment, Account
from db.local_settings.models import Languages
from db.account.models import Translation
from itertools import permutations
from db.db_utils import bulk_upsert, set_tenant_for_request


def upload_translates(df, tenant, assigned_to):
    set_tenant_for_request(tenant.id)
    unique_field = ["_id"]
    translate_model_fields = [f.name for f in Translation._meta.get_fields()]
    translate_fields = ["name", "description", "assigned_to", "lang"]
    locales = Languages.objects.values_list("locale", flat=True)

    translates_df = pd.DataFrame(columns=[*unique_field, *translate_fields])
    for l in locales:
        locale = f"_{l}"
        df_fields = []
        for f in translate_fields:
            df_fields.append(f"{f}{locale}")
        temp = df[df.columns.intersection(df_fields)].reset_index()
        temp.columns = temp.columns.str.replace(f"{locale}", "")
        temp["lang"] = l
        translates_df = pd.concat([translates_df, temp])

    if translates_df.empty:
        return

    translates_df["assigned_to"] = "account"

    translate_data = bulk_upsert(
        Translation,
        list(translates_df[translate_fields].columns),
        [tuple(x) for x in translates_df[translate_fields].values.tolist()],
        f"{tenant.db_name}_schema",
        conflict_on=["name", "lang", "assigned_to"],
        do_update=True,
        returning=["id"],
    )

    translates_df["translation_id"] = translate_data
    result = translates_df
    return translates_df


def upload_account_csv(request):
    tenant = request.tenant

    account_fields = [f.name for f in Account._meta.get_fields()]
    file = request.FILES.get("file")
    df = (
        pd.read_csv(file, index_col=False, delimiter=";")
        .rename(columns={"createdAt": "created_at", "updatedAt": "updated_at"})
        .dropna(subset=["account_number"])
        .set_index("_id")
    )

    crated_account_translates = upload_translates(df, tenant, "account")
    created_translates_ids = pd.DataFrame(data=crated_account_translates[["_id", "translation_id"]])
    grouped_account_translate = crated_account_translates.groupby("_id").agg({"name": "first", "description": "first"})
    accounts_df = df.merge(grouped_account_translate, on="_id", how="left")
    inserted_accounts = pd.DataFrame(data=accounts_df.index)
    accounts_df = accounts_df[accounts_df.columns.intersection(account_fields)]
    accounts_df = accounts_df.where(pd.notnull(accounts_df), None)

    translate_data = bulk_upsert(
        Account,
        list(accounts_df.columns),
        [tuple(x) for x in accounts_df.values.tolist()],
        f"{tenant.db_name}_schema",
        conflict_on=["name"],
        do_update=True,
        returning=["id"],
    )

    inserted_accounts["account_id"] = translate_data
    translates = created_translates_ids.merge(inserted_accounts, on="_id", how="outer")[
        ["translation_id", "account_id"]
    ]
    account_translate = Account.translations.through

    bulk_upsert(
        account_translate,
        list(translates.columns),
        [tuple(x) for x in translates.values.tolist()],
        f"{tenant.db_name}_schema",
        conflict_on=["translation_id", "account_id"],
    )

