# Generated by Django 3.1.6 on 2021-03-28 19:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0001_initial'),
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order_type', models.CharField(choices=[('sale_order', 'Sale order log'), ('purchase_order', 'Purchase order log')], max_length=128)),
                ('data', models.JSONField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HelpDesk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('uid', models.CharField(max_length=128, unique=True)),
                ('status', models.CharField(max_length=24)),
                ('order_date', models.DateTimeField(null=True)),
                ('shipment_service', models.CharField(max_length=128, null=True)),
                ('tracking_code', models.CharField(max_length=128, null=True)),
                ('notes', models.TextField(null=True)),
                ('comment', models.TextField(null=True)),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('files', models.ManyToManyField(blank=True, related_name='desks', to='product.File')),
                ('orders', models.ManyToManyField(blank=True, related_name='desks', to='orders.SalesOrder')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]