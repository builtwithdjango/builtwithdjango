from django.core.mail import send_mail


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
