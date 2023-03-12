# from Will Vincent tutorial -> https://learndjango.com/tutorials/django-markdown-tutorial

import markdown as md
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

extension_configs = {
    "markdown.extensions.codehilite": {"css_class": "codehilite", "linenums": False, "guess_lang": False}
}


@register.filter()
@stringfilter
def markdown(value):
    return md.markdown(
        value,
        extensions=["markdown.extensions.codehilite", "markdown.extensions.fenced_code"],
        extension_configs=extension_configs,
    )
