import os

from django import template
from django.conf import settings

register = template.Library()

@register.filter()
def media_filter(path):
    if path:
        path = str(path).lstrip('/')
        return os.path.join(settings.MEDIA_URL, path)
    return "#"