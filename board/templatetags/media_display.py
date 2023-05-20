from django import template
from django.conf import settings

register = template.Library()

@register.filter
def media_url(value):
    if settings.REMOTE_MEDIA and value["remote_url"]:
        url = value["remote_url"]
    else:
        url = value["url"]

    if settings.MEDIA_URL_REWRITE:
        for k, v in settings.MEDIA_URL_REWRITE_RULES.items():
            if url.startswith(k):
                url = url.replace(k, v, 1)

    return url