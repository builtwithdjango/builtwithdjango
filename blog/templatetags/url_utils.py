from django import template

register = template.Library()


@register.filter
def replace_quotes(value):
    return value.replace('"', "'")
