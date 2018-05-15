from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name='hyphen', is_safe=True)
@stringfilter
def hyphen(value):
    return value.replace(' ', '-')


@register.filter(name='zip')
def zip_lists(a, b):
    return zip(a, b)
