import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.errors import DuplicateDatabase, DuplicateTable

import subprocess
import shlex

import json

from django.conf import settings
from django.db import connection

from db.core.models import Tenant


def run_command(command):
    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    print(proc_stdout)


def create_tenant_schema(company_name):
    schema_name = company_name.lower().replace(" ", "_")
    final_schema_name = schema_name + "_schema"

    db_settings = settings.DATABASE_HOST_SETTINGS 
    HOST = db_settings['HOST']
    PASSWORD = db_settings['PASSWORD']
    PORT = db_settings['PORT']
    USER = db_settings['USER']
    DB_NAME = db_settings["NAME"]

    con = psycopg2.connect(
        database=DB_NAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    with con.cursor() as cur:
        cur.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {};").format(
            sql.Identifier(final_schema_name))
        )

    tenant_db = {
        schema_name: dict(
            OPTIONS={'options': f"-c search_path={final_schema_name}"},
            SCHEMA_NAME=final_schema_name,
            **db_settings
        )
    }
    tenant = Tenant.objects.get_or_create(
        company_name=company_name, 
        db_name=schema_name,
        db_conf=tenant_db    
    )
    
    if tenant[1]:
        run_command(f"pipenv run python {settings.BASE_DIR}/manage.py runscript update_db_conf")
        run_command(f"pipenv run python {settings.BASE_DIR}/manage.py migrate --database {schema_name}")
    
    return tenant


def set_tenant_for_request(tenant_id):
    tenant = Tenant.objects.get(id=tenant_id)
    schema_name = tenant.db_conf[tenant.db_name]['SCHEMA_NAME']
    with connection.cursor() as cursor:
        cursor.execute(f"SET search_path to {schema_name}")


UPDATE_SQL_QUERY = """
    WITH update_tb as (
        INSERT INTO {schema}.{table_name} ({fields_names})
        VALUES {placeholders}
        ON CONFLICT ({conflicts})
        DO UPDATE SET {set_values} 
        RETURNING {return_fields}
    ) SELECT ARRAY_AGG({agg_func})
    FROM update_tb;
"""

IGNORE_SQL_QUERY = """
    INSERT INTO {schema}.{table_name} ({fields_names})
    VALUES {placeholders}
    ON CONFLICT ({conflicts})
    DO NOTHING;
"""

def bulk_upsert(model, fields, values, schema_name, conflict_on=[], do_update=False, returning=["id"]):
    table = model._meta.db_table

    fields_names = ", ".join(fields)
    conflicts = ", ".join(conflict_on)
    placeholders = ("%s, " * len(values))[:-2]
    set_values = ", ".join([
        "{field}=EXCLUDED.{field}".format(field=f) for f in fields if f not in conflict_on
    ])
    return_fields = ", ".join(returning)
    if len(returning) > 1:
        agg_func = " || ',' || ".join(returning)
    else: 
        agg_func = returning[0]
    
    sql = IGNORE_SQL_QUERY
    if do_update:
        sql = UPDATE_SQL_QUERY

    sql_query = sql.format(
        schema=schema_name,
        table_name=table,
        fields_names=fields_names, 
        placeholders=placeholders,
        set_values=set_values,
        conflicts=conflicts, 
        return_fields=return_fields,
        agg_func=agg_func
    )
    result = [None]
    with connection.cursor() as cursor:
        cursor.execute(sql_query, values)
        if do_update:
            result = cursor.fetchall()[0]

    return result[0]