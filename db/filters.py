from rest_framework.filters import BaseFilterBackend
from distutils.util import strtobool
from django.db.models import Q
import datetime
from dateutil.relativedelta import relativedelta
from rest_framework.exceptions import ValidationError
from .utils import get_user_permission
from db.core import PermissionsTypes

class ConditionFilter(BaseFilterBackend):
    #TODO - фільтрація по даті
    lookups = {
        ">": "__gt=",
        "<": "__lt=",
        "=": "=",
        "__contains=": "__contains=",
    }
    negative_lookups = {
        "!=": "=",
        "__notcontains=": "__contains="
    }
    condition_markers = {
        "and": "&&",
        "or": "||",
        "not": "!!"
    }

    def get_filter_str(self, request):
        filter_params = request.query_params.get("filters")
        if not filter_params:
            return
        filter_params = filter_params.split(",")
        filter_str = ""
        for param in filter_params:
            splited = param.split("$")
            if len(splited) > 1:
                filter_str += splited[0] + self.condition_markers[splited[1]]
            else:
                filter_str += splited[0] + self.condition_markers["and"]
        return filter_str

    def validate_field(self, field, lookup):
        boolvalues = ["true", "True", "t", "false", "False", "f"]
        field_name, value = tuple(field.split(lookup))
        if value in boolvalues:
            value = strtobool(value)

        if lookup in self.lookups.keys():
            return field_name + self.lookups[lookup] + f"'{value}'"
        return f"~Q({field_name}{self.negative_lookups[lookup]}'{value}')"

    def transform_conditions(self, fields):
        transformed_fields = []
        for field in fields:
            for lookup in list(self.lookups.keys()) + list(self.negative_lookups.keys()):
                if lookup in field:
                    transformed_fields.append(f"Q({self.validate_field(field, lookup)})")
                    
        return transformed_fields

    def get_conditions(self, filter_str):
        before_condition = filter_str
        conditions = ""
        not_condition = filter_str.split("!!")
        if len(not_condition) > 1:
            before_condition = not_condition[0].strip()
            after_not_condition = self.get_conditions("!!".join(not_condition[1:]))
            conditions += f", ~Q({after_not_condition})"
        
        or_condition = before_condition.split("||")
        if len(or_condition) > 1:
            before_condition = or_condition[0].strip()
            after_or_condition = self.get_conditions("||".join(or_condition[1:]))
            conditions = f"| Q({after_or_condition})" + conditions
        
        and_conditions = [x.strip() for x in before_condition.split("&&")]
        transformed_conditions = ', '.join(self.transform_conditions(and_conditions))
        conditions = f"{transformed_conditions} {conditions}".strip()
        return conditions

    def filter_queryset(self, request, queryset, view):
        filter_str = self.get_filter_str(request)
        if not filter_str:
            return queryset

        conditions_str = self.get_conditions(filter_str)
        conditions = eval(conditions_str)    
        try:
            return queryset.filter(*conditions)    
        except TypeError:
            return queryset.filter(conditions)


class DateFilter(BaseFilterBackend):
    times = {
        "today": datetime.datetime.now(),
        "sameDayLastMonth": datetime.datetime.now() - relativedelta(months=1),
        "sameDayLastQuater": datetime.datetime.now() - relativedelta(months=3)
    }
    lookups = {
        "curr_month": (times["sameDayLastMonth"], times["today"]),
        "last_month": (times["today"] - relativedelta(months=2), times["sameDayLastMonth"]), 
        "curr_quater": (times["sameDayLastQuater"], times["today"]),
        "last_quater": (times["today"] - relativedelta(months=6), times["sameDayLastQuater"])
    }

    def get_condition(self, filter_str, date_field):
        if filter_str in self.lookups.keys():
            return {f"{date_field}__range": self.lookups[filter_str]}
        
        return {f"{date_field}__year": filter_str}

    def filter_queryset(self, request, queryset, view):
        filter_str = request.query_params.get("dateRange")
        date_field = getattr(view, "date_filter_field", None)
        if not filter_str or not date_field:
            return queryset
        filter = self.get_condition(filter_str, date_field)
        return queryset.filter(**filter)


class EdgeDateFilter(BaseFilterBackend):
    
    def filter_queryset(self, request, queryset, view):
        date_field = getattr(view, "edges_date_field", None)
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")

        if not date_from and not date_to:
            return queryset

        if not date_field:
            return queryset
        
        filters = {}
        if date_from:
            date_from = datetime.datetime.strptime(date_from, "%y-%m-%dT%H:%M:%SZ")
            filters.update({f"{date_field}__gte": date_from})
        if date_to:
            date_to = datetime.datetime.strptime(date_to, "%y-%m-%dT%H:%M:%SZ")
            filters.update({f"{date_field}__gte": date_to})

        return queryset.filter(**filters)


class PermissionFilter(BaseFilterBackend):
    
    def filter_queryset(self, request, queryset, view):
        user = request.user
        permission = get_user_permission(request, view)
        if not permission:
            return queryset
        
        if permission.rights in [PermissionsTypes.NONE, PermissionsTypes.ADMIN, PermissionsTypes.READ_ONLY]:
            return queryset
        
        if permission.rights == PermissionsTypes.CREATOR:
            return queryset.filter(user_owner=user.id)

        return queryset   
    