from django import template

register = template.Library()


@register.filter
def get_item(mapping, key):
    if mapping is None:
        return ''
    return mapping.get(key, '')


@register.filter
def contains(value, item):
    return isinstance(value, list) and item in value
