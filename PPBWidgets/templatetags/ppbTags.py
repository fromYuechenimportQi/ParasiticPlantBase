from django.db.models.query import QuerySet
from django.template import Library

register = Library()


@register.filter
def is_queryset_or_list(value):
    return isinstance(value, QuerySet) or isinstance(value,list)

@register.filter
def replace_space_to_underline(value):
    return value.replace(" ","_")

@register.filter
def get_value_from_dict(dict_obj, key):
    return dict_obj.get(key)