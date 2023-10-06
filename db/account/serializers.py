from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from db.core.serializers import RegisterSerializer
from .models import Translation, Address, Customer
from django.db.models import Q


class AuthCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "username",
            "password"
        ]
        extra_kwargs = {
            "username": {"validators": []}
        }
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        if username and password:
            users = self.Meta.model.objects.filter(
                Q(username=username) |
                Q(phone=username) |
                Q(email=username)
            )
            if users.exists():
                user = users.first()
                valid = user.check_password(password)
                if not valid:
                    raise ValidationError("Password is not correct")
            else:
                raise ValidationError("User does not exists")
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class CustomerRegisterSerializer(RegisterSerializer):

    def save(self, request):
        data = self.validated_data
        password = data.pop("password")

        user = Customer(
            **data,
            is_active = True,
            tenant_id = request.tenant_id,
            is_confirmed=True
        )
        user.set_password(password)
        try:
            user.save()
        except:
            raise serializers.ValidationError("User already exists")
        
        return user


class CustomerSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=128, read_only=True)
    class Meta:
        model = Customer
        fields = [
            "id",
            "phone",
            "username",
            "email",
            "payment_account", 
            "street", 
            "street_number",
            "city", 
            "country",
            "zip"
        ]
        extra_kwargs = {
            "username": {"validators": []}
        }

    def save(self):
        self.validated_data["tenant_id"] = self.context["request"].tenant_id
        user_qs = self.Meta.model.objects.filter(
            Q(username=self.validated_data["username"]) |
            Q(email=self.validated_data["email"]) |
            Q(phone=self.validated_data["phone"])
        )
        if user_qs.exists():
            user_qs.update(**self.validated_data)
            return user_qs.first()
        return super().save()

    # def save(self):
    #     address_serializer = AddressSerializer(data=self.validated_data)
    #     address_serializer.is_valid()
    #     address = address_serializer.save()
    #     self.clear_data()

    #     instance = super().save()
        
    #     user_qs = self.Meta.model.objects.filter(
    #         Q(name=self.validated_data["name"]) |
    #         Q(email=self.validated_data["email"]) |
    #         Q(phone=self.validated_data["phone"])
    #     )
    #     if user_qs.exists():
    #         instance = user_qs.first()
        
    #     instance.address = address
    #     instance.save()

    #     return instance
        
    # def clear_data(self):
    #     model_fields = [f.name for f in self.Meta.model._meta.fields]
    #     for x in list(self.validated_data.keys()):
    #         if x not in model_fields:
    #             self.validated_data.pop(x)
