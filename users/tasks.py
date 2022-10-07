from allauth.account.signals import email_confirmed
from django.core.mail import send_mail
from django.dispatch import receiver

from newsletter.tasks import add_email_to_revue


def notify_of_new_user(instance):
    message = f"""
      We have a new user.
      Instance: {instance}
    """
    send_mail(
        "New User",
        message,
        "rasul@builtwithdjango.com",
        ["rasul@builtwithdjango.com"],
        fail_silently=False,
    )


@receiver(email_confirmed)
def email_confirmation_callback(sender, **kwargs):
    add_email_to_revue(kwargs["email_address"], double_opt_in=False)
