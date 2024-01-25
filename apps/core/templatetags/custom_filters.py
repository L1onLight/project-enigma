from django import template

register = template.Library()


@register.filter
def remove_symbols(value, symbols):
    print(f"value:{value} | symbols:{symbols}")
    for symbol in symbols:
        value = value.replace(symbol, '')
    return value
