from django.apps import AppConfig


class OrdersConfig(AppConfig):
    name = 'db.orders'

    def ready(self):
        import db.orders.signals
