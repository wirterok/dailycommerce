import json

from rest_framework import serializers 
from db.helper_serializers import BaseTranslateSerializer
from db.orders.models import PurchaseOrder, SalesOrder, Expense
from . import models as payment_models


class AccountSerializer(BaseTranslateSerializer):
    payment_accounts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = payment_models.Account
        fields = "__all__"
        read_only_fields = ["created_at"]
    
    def is_valid(self, raise_exception=False):
        if default_for := self.initial_data.get("default_for", []):
            default_for = json.dumps(default_for)
        else:
            default_for = json.dumps([])

        self.initial_data["default_for"] = default_for
        super().is_valid(raise_exception)
  
    def to_representation(self, obj):
        data = super().to_representation(obj)
        json_dec = json.decoder.JSONDecoder()
        
        try: 
            data['default_for'] = json_dec.decode(data['default_for'])
        except:
            pass
        return data


class PaymentAccountSerializer(BaseTranslateSerializer):
    account = serializers.PrimaryKeyRelatedField(many=False, queryset=payment_models.Account.objects.all())
    
    class Meta:
        model = payment_models.PaymentAccount
        fields = "__all__"
        read_only_fields = ["created_at"]


class PaymentSerializer(BaseTranslateSerializer):
    account = serializers.PrimaryKeyRelatedField(
        many=False, queryset=payment_models.PaymentAccount.objects.all()
    )
    # reference_type = serializers.ChoiceField(choices=["purchase_order", "sale_order", "expense"])
    reference_type = serializers.CharField(max_length=128, write_only=True)
    reference_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = payment_models.Payment
        fields = [
            "name",
            "description", 
            "type",
            "amount",
            "status",
            "note",
            "receiver_account",
            "marketplace_id",
            "bookkeeping_status",
            "is_locked",
            "account",
            "translations",
            "reference_type",
            "reference_id"
        ]

    def save(self):    
        reference_type = self.validated_data.pop("reference_type")
        reference_id = self.validated_data.pop("reference_id")
        instance = super().save()
        self.handle_reference(instance, reference_type, reference_id)
        return instance

    @staticmethod
    def handle_reference(payment, reference_type, reference_id):
        if reference_type == "purchase_order":
            order = PurchaseOrder.objects.get(id=reference_id)
            order.payment_id = payment.id
            order.save()
        elif reference_type == "sale_order":
            order = SalesOrder.objects.get(id=reference_id)
            order.payment_id = payment.id
            order.save()
        elif reference_type == "expense":
            expense = Expense.objects.get(id=reference_id)
            expense.payment_id = payment.id
            expense.save()
        
