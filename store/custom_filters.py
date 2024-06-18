from django import template

register = template.Library()

@register.filter(name='mult')
def mult(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
