from django import template
from django.template.defaultfilters import stringfilter
import markdown

register = template.Library()

@register.filter
@stringfilter
def render_markdown(value):
    """Конвертирует Markdown в HTML"""
    md = markdown.Markdown(extensions=[
        'extra',
        'codehilite',
        'toc',
        'nl2br',  # преобразует переносы строк в <br>
    ])
    return md.convert(value)