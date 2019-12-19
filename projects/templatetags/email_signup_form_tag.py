from django import template
from django.forms import modelform_factory
from newsletter.models import Emails
from newsletter.views import NewsletterSignupForm

register = template.Library()

@register.inclusion_tag('template_tags/newsletter_signup_form.html')
def get_signup_form():
    return {
        'form': NewsletterSignupForm
        }
