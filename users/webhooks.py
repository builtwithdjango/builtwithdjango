"""
Stripe webhook handlers for Built with Django.

This module handles all Stripe webhook events using dj-stripe's signal-based approach.
Each handler is registered using the @djstripe_receiver decorator and processes
specific Stripe events.

For more information on dj-stripe webhooks:
https://dj-stripe.dev/docs/dev/usage/webhooks
"""

from functools import partial

import stripe
from django.db import transaction
from django.http import HttpResponse
from djstripe import models, settings as djstripe_settings
from djstripe.event_handlers import djstripe_receiver

from builtwithdjango.utils import get_builtwithdjango_logger
from users.models import CustomUser

logger = get_builtwithdjango_logger(__name__)
stripe.api_key = djstripe_settings.djstripe_settings.STRIPE_SECRET_KEY


@djstripe_receiver("checkout.session.completed")
def handle_checkout_session_completed(sender, **kwargs):
    """
    Handle successful checkout session completion.

    This handler routes the event to the appropriate processor based on the
    price_id in the session metadata:
    - PRO user upgrades
    - Django Devs subscriptions
    - Job board postings

    Args:
        sender: The signal sender (Event model)
        **kwargs: Additional keyword arguments including the event

    Returns:
        HttpResponse: HTTP 200 status response
    """
    event = kwargs.get("event")

    # Get price IDs from database
    pro_price_id = models.Price.objects.get(nickname="pro").id
    devs_price_id = models.Price.objects.get(nickname="django_devs").id
    job_price_id = models.Price.objects.get(nickname="job").id

    event_price_id = event.data["object"]["metadata"].get("price_id")
    logger.info(f"Received checkout.session.completed event for Price ID: {event_price_id}")

    if event_price_id == pro_price_id:
        logger.info("Processing PRO user purchase")
        process_pro_user_upgrade(event)
    elif event_price_id == devs_price_id:
        logger.info("Processing Django Devs subscription purchase")
        process_django_devs_subscription(event)
    elif event_price_id == job_price_id:
        logger.info("Processing Job Board purchase")
        process_job_board_payment(event)
    else:
        logger.warning(f"Unrecognized price_id in checkout.session.completed: {event_price_id}")

    return HttpResponse(status=200)


def process_pro_user_upgrade(event):
    """
    Process a PRO user upgrade purchase.

    This function syncs the customer data from Stripe and schedules the user
    upgrade to happen after the database transaction commits.

    Args:
        event: The Stripe Event object containing checkout session data
    """
    if event.type == "checkout.session.completed":
        customer_id = event.data["object"]["customer"]
        logger.info(f"Upgrading Customer: {customer_id}")

        # Sync customer data from Stripe
        models.Customer.sync_from_stripe_data(stripe.Customer.retrieve(customer_id))

        # Schedule user upgrade after transaction commit
        transaction.on_commit(partial(upgrade_user_to_pro, event))


def upgrade_user_to_pro(event):
    """
    Upgrade a user to PRO subscription level.

    This function is called after the database transaction commits to ensure
    all Stripe data has been synced before updating the user.

    Args:
        event: The Stripe Event object containing user metadata
    """
    user_id = event.data["object"]["metadata"]["pk"]
    logger.info(f"Upgrading user {user_id} to PRO subscription level")

    try:
        user = CustomUser.objects.get(pk=user_id)
        user.subscription_level = "PRO"
        user.save()
        logger.info(f"Successfully upgraded user {user_id} to PRO")
    except CustomUser.DoesNotExist:
        logger.error(f"User {user_id} not found for PRO upgrade")
    except Exception as e:
        logger.error(f"Error upgrading user {user_id} to PRO: {str(e)}")


def process_django_devs_subscription(event):
    """
    Process a Django Devs subscription purchase.

    This function syncs the subscription data from Stripe and schedules the
    subscription flag update to happen after the database transaction commits.

    Args:
        event: The Stripe Event object containing checkout session data
    """
    if event.type == "checkout.session.completed":
        subscription_id = event.data["object"]["subscription"]
        logger.info(f"Processing Django Devs subscription: {subscription_id}")

        # Sync subscription data from Stripe
        models.Subscription.sync_from_stripe_data(stripe.Subscription.retrieve(subscription_id))

        # Schedule subscription flag update after transaction commit
        transaction.on_commit(partial(activate_django_devs_subscription, event))


def activate_django_devs_subscription(event):
    """
    Activate Django Devs subscription flag for a user.

    This function is called after the database transaction commits to ensure
    all Stripe subscription data has been synced before updating the user.

    Args:
        event: The Stripe Event object containing user metadata
    """
    user_id = event.data["object"]["metadata"]["user_id"]
    logger.info(f"Activating Django Devs subscription for user {user_id}")

    try:
        user = CustomUser.objects.get(id=user_id)
        user.has_active_django_devs_subscription = True
        user.save()
        logger.info(f"Successfully activated Django Devs subscription for user {user_id}")
    except CustomUser.DoesNotExist:
        logger.error(f"User {user_id} not found for Django Devs subscription activation")
    except Exception as e:
        logger.error(f"Error activating Django Devs subscription for user {user_id}: {str(e)}")


def process_job_board_payment(event):
    """
    Process a Job Board posting payment.

    This function schedules the job approval to happen after the database
    transaction commits.

    Args:
        event: The Stripe Event object containing checkout session data
    """
    if event.type == "checkout.session.completed":
        job_id = event.data["object"]["metadata"]["pk"]
        logger.info(f"Processing Job Board payment for job {job_id}")

        # Schedule job approval after transaction commit
        transaction.on_commit(partial(approve_paid_job, event))


def approve_paid_job(event):
    """
    Approve and mark a job as paid.

    This function is called after the database transaction commits to update
    the job's paid and approved status.

    Args:
        event: The Stripe Event object containing job metadata
    """
    from jobs.models import Job

    job_id = event.data["object"]["metadata"]["pk"]
    logger.info(f"Approving paid job {job_id}")

    try:
        job = Job.objects.get(pk=job_id)
        job.paid = True
        job.approved = True
        job.save()
        logger.info(f"Successfully approved paid job {job_id}")
    except Job.DoesNotExist:
        logger.error(f"Job {job_id} not found for approval")
    except Exception as e:
        logger.error(f"Error approving job {job_id}: {str(e)}")


# Additional webhook handlers can be added here as needed
# Examples:
#
# @djstripe_receiver("customer.subscription.deleted")
# def handle_subscription_deleted(sender, **kwargs):
#     """Handle subscription cancellation."""
#     event = kwargs.get("event")
#     subscription_id = event.data["object"]["id"]
#     # Process subscription cancellation
#     pass
#
# @djstripe_receiver("invoice.payment_failed")
# def handle_payment_failed(sender, **kwargs):
#     """Handle failed payment."""
#     event = kwargs.get("event")
#     invoice_id = event.data["object"]["id"]
#     # Process payment failure
#     pass
