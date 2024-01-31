from django import template

register = template.Library()


@register.filter
def remove_symbols(value, symbols):
    for symbol in symbols:
        value = value.replace(symbol, '')
    return value
