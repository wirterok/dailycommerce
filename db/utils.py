from rest_framework.serializers import ValidationError
from django.conf import settings
from db.settings.models import SMTP


def get_ids(model, fields: dict, search_fields: list):
    ids = []
    for field in fields:
        for f in search_fields:
            if f not in list(field.keys()):
                raise ValidationError(f"Search field {f} doesnt exists in passed data")
        
        filters = {k:field[k] for k in search_fields if field[k]}
        qs = model.objects.filter(**filters)
        if qs.exists():
            ids += qs.values_list("id", flat=True)
        else:
            new_instance = model.objects.create(**field)
            ids.append(new_instance.id)
    return ids


def apply_key(container, key, value):
    def apply(x):
        x[key] = value
        return x
    return map(apply, container)


def write_instance(data, serializer_class, many=False, **kwargs):
    if many:
        field = kwargs.pop("extra_field", None)
        value = kwargs.pop("extra_field_value", None)
        if not field or not value:
            raise ValidationError("extra field and value must be provided")
        data = list(apply_key(data, field, value))
    
    context = kwargs.pop("context", None)
    serializer = serializer_class(data=data, many=many, context=context)
    if not serializer.is_valid():
        raise ValidationError(serializer.errors)
    return serializer.save()


def get_user_permission(request, view):
    model_name = view.model_class.__name__.lower()
    user_group = request.user.groups
    if not user_group:
        return None
    permissions = user_group.permissions.filter(model_name=model_name)
    if not permissions:
        return None
    return permissions.first()


def compare_dicts(obj1, obj2):
    same_fields = set(obj1.keys()).intersection(obj2.keys())
    update_fields = {}
    for k in same_fields:
        if obj1[k] != obj2[k]:
            update_fields[k] = obj2[k]

    return update_fields
