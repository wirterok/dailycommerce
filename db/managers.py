from db.orders.models import PurchaseOrder, SalesOrder, ProductUnit
from django.db.models import Sum
from dateutil.relativedelta import relativedelta
import pandas as pd
import datetime


class DashnoardManager:
    def __init__(self, request):
        self.request = request
        self.purchase_orders = PurchaseOrder.objects.filter(in_trash=False)
        self.sales_orders = SalesOrder.objects.filter(in_trash=False)
        self.month_names = {
            "1": "Jan.",
            "2": "Feb.",
            "3": "Mar.",
            "4": "Apr.",
            "5": "May",
            "6": "June",
            "7": "July",
            "8": "Aug.",
            "9": "Sept.",
            "10": "Oct.",
            "11": "Now.",
            "12": "Dec.",
        }
        self.date_from = datetime.date.today() - relativedelta(years=1)
        self.date_filter = {"created_at__gte": self.date_from}

    def group_by_month(self, df, column, aggregation: dict):
        df["month"] = df[column].apply(lambda x: self.month_names[str(x.month)])
        new_df = df.groupby(["month"]).agg(aggregation)
        return new_df

    def get_chart(self):
        final_df = pd.DataFrame(
            data={"month": list(self.month_names.values()), "purchaseOrders": 0, "salesOrders": 0}
        ).set_index("month")

        purchase_qs = PurchaseOrder.objects.filter(**self.date_filter).values("created_at", "total_price")
        sales_qs = SalesOrder.objects.filter(**self.date_filter).values("created_at", "total_price")

        aggregation = {"total_price": "sum"}
        if purchase_qs.exists():
            purchase_df = pd.DataFrame(purchase_qs)
            purchase_df = self.group_by_month(purchase_df, "created_at", aggregation).rename(
                columns={"total_price": "purchaseOrders"}
            )
            final_df.update(purchase_df, join="left", overwrite=True)

        if sales_qs.exists():
            sales_df = pd.DataFrame(sales_qs)
            sales_df = self.group_by_month(sales_df, "created_at", aggregation).rename(
                columns={"total_price": "salesOrders"}
            )
            final_df.update(sales_df, join="left", overwrite=True)

        final_df["profit"] = final_df[["purchaseOrders", "salesOrders"]].apply(
            lambda x: x["salesOrders"] - x["purchaseOrders"], axis=1
        )
        return final_df.reset_index().to_dict("records")

    def get_inventory(self):
        final_df = pd.DataFrame(data={"month": list(self.month_names.values()), "purchasePrice": 0, "averagePrice": 0}).set_index("month")
        unit_qs = ProductUnit.objects.filter(**self.date_filter).values("created_at", "selling_price", "purchase_price")

        aggregation = {"purchase_price": "sum", "selling_price": "mean"}
        if unit_qs.exists():
            units_df = pd.DataFrame(unit_qs).fillna(0)
            units_df[["purchase_price", "selling_price"]] = units_df[["purchase_price", "selling_price"]].astype(float)
            units_df = self.group_by_month(units_df, "created_at", aggregation).rename(
                columns={"selling_price": "averagePrice", "purchase_price": "purchasePrice"}
            )
            final_df.update(units_df, join="left", overwrite=True)
        return final_df.reset_index().to_dict("records")

    def get_user_data(self):
        purchase_total_price = (
            self.purchase_orders.filter(user_owner=self.request.user.id)
            .values("user_owner")
            .annotate(total=Sum("total_price"))
            .values_list("total", flat=True)
        )
        sales_total_price = (
            self.sales_orders.filter(user_owner=self.request.user.id)
            .values("user_owner")
            .annotate(total=Sum("total_price"))
            .values_list("total", flat=True)
        )
        return {
            "id": self.request.user.id,
            "salesOrder": sum(purchase_total_price),
            "purchaseOrder": sum(sales_total_price),
        }

    def get_logs(self):
        purchase_orders = self.purchase_orders[:25].values("created_at", "status", "uid", "user_owner")
        sales_orders = self.sales_orders[:25].values("created_at", "status", "uid", "user_owner")
        sales_df = pd.DataFrame(sales_orders)
        purchase_df = pd.DataFrame(purchase_orders)
        if purchase_orders.exists():
            purchase_df["created_at"] = purchase_df["created_at"].apply(lambda x: x.strftime("%Y-%m-%d"))
        if sales_orders.exists():
            sales_df["created_at"] = sales_df["created_at"].apply(lambda x: x.strftime("%Y-%m-%d"))
        return {"purchaseOrder": purchase_df.to_dict("records"), "salesOrder": sales_df.to_dict("records")}

    def result(self):
        result = {
            "inventory": self.get_inventory(),
            "chart": self.get_chart(),
            "logs": self.get_logs(),
            "user_data": self.get_user_data(),
        }
        return result