from db.core.models import Tenant
from django.conf import settings
import json
import os


def get_tenant_databases():
    databases = Tenant.objects.all().values_list("db_conf", flat=True)
    for db in [x for x in databases if x]:
        for k, v in db.items():
            yield k, v     


def run():
    tenant_databases = {k:v for k,v in get_tenant_databases()}
    with open(os.path.join(settings.BASE_DIR, settings.DB_CONFIG_FILE), "w") as jfile:
        json.dump(tenant_databases, jfile, indent=4)

