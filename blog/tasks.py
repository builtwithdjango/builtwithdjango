from django.core.mail import send_mail


def notify_admin_of_guide_comment(instance):
    message = f"""
      {instance.author} left a comment on post {instance.post.title}.
      Comment: {instance.comment}
    """

    send_mail(
        f"New Comment on post {instance.post.title}",
        message,
        "Built with Django <rasul@builtwithdjango.com>",
        ["Built with Django <rasul@builtwithdjango.com>"],
        fail_silently=False,
    )
