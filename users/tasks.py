from allauth.account.signals import email_confirmed, user_signed_up
from django.core.mail import send_mail
from django.dispatch import receiver

from newsletter.tasks import add_email_to_revue


@receiver(user_signed_up)
def notify_of_new_user(sender, **kwargs):
    message = f"""
      Sender: {sender}
      We have a new user: {kwargs["user"]}
    """
    send_mail(
        f"New User: {kwargs['user']}",
        message,
        "rasul@builtwithdjango.com",
        ["rasul@builtwithdjango.com"],
        fail_silently=False,
    )


@receiver(email_confirmed)
def email_confirmation_callback(sender, **kwargs):
    add_email_to_revue(kwargs["email_address"], double_opt_in=False)
