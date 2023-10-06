from django.core.management.commands.migrate import Command as MigrationCommand

from django.db import connection
from db.core.models import Tenant


class Command(MigrationCommand):
    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            schemas = Tenant.objects.all().values_list("db_name", flat=True)
            for schema in schemas:
                cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}_schema")
                cursor.execute(f"SET search_path to {schema}_schema")
                super(Command, self).handle(*args, **options)