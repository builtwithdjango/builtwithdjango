import stripe
from django.conf import settings
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from newsletter.views import NewsletterSignupForm

from .forms import PostJob
from .models import Job


class JobListView(ListView):
    model = Job
    template_name = "jobs/all_jobs.html"
    queryset = Job.objects.filter(approved=True).order_by("-created_datetime")[:30]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context


class JobDetailView(DetailView):
    model = Job
    template_name = "jobs/job_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context


class JobCreateView(CreateView):
    model = Job
    form_class = PostJob
    template_name = "jobs/post-job.html"

    def get_success_url(self):
        return reverse("stripe_checkout_session", kwargs={"pk": self.object.id})


class ThankYouView(TemplateView):
    template_name = "jobs/post-job-thank-you.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context


@csrf_exempt
def create_checkout_session(request, pk):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session = stripe.checkout.Session.create(
        success_url=request.build_absolute_uri(reverse_lazy("job_thank_you")) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse_lazy("job_thank_you")) + "?status=failed",
        mode="payment",
        line_items=[
            {
                "quantity": 1,
                "price": settings.POST_JOB_PRODUCT_ID,
            }
        ],
        metadata={"pk": pk},
    )
    return redirect(checkout_session.url, code=303)


@csrf_exempt
def webhook(request):
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_ENDPOINT_SECRET)
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    except:
        return

    if event.type == "checkout.session.completed":
        job_id = event["data"]["object"]["metadata"]["pk"]
        job = Job.objects.get(pk=job_id)
        job.paid = True
        job.approved = True
        job.save()
        return JsonResponse({"event": event})
    else:
        print("Unhandled event type {}".format(event.type))
