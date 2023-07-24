from allauth.account.signals import email_confirmed, user_signed_up
from django.conf import settings
from django.core.mail import send_mail
from django.dispatch import receiver

from newsletter.tasks import add_email_to_buttondown


# @receiver(user_signed_up)
def notify_of_new_user(sender, **kwargs):
    message = f"""
      Sender: {sender}
      We have a new user: {kwargs["user"]}
    """
    send_mail(
        f"New User: {kwargs['user']}",
        message,
        "Built with Django <rasul@builtwithdjango.com>",
        ["Built with Django <rasul@builtwithdjango.com>"],
        fail_silently=False,
    )


@receiver(email_confirmed)
def email_confirmation_callback(sender, **kwargs):
    if not settings.DEBUG:
        add_email_to_buttondown(kwargs["email_address"], tag="user")
