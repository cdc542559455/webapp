from django import template
register = template.Library()

@register.filter(name='counter')
def specialacount(val):
    return val*2+15

@register.filter(name='counter2')
def specialacount2(val):
    return val*2+16