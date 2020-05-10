from django.views.generic import ListView, DetailView, TemplateView, CreateView
from django.views.generic.edit import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from .models import Project, Maker
from django.urls import reverse_lazy

from newsletter.views import NewsletterSignupForm
from newsletter.models import Emails
from .forms import AddProject


class ProjectListView(ListView):
    model = Project
    template_name = 'home.html'
    ordering = ['-date_added']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = NewsletterSignupForm

        return context

class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = NewsletterSignupForm

        return context


class EmailFormView(SuccessMessageMixin, CreateView):
    form_class = NewsletterSignupForm
    model = Emails

    def form_valid(self, form):
        self.object = form.save()
        
        emailoctopus_api_key = settings.EMAILOCTOPUS_API
        list_id = settings.OCTO_LIST_ID

        data = {
            "api_key": emailoctopus_api_key,
            "email_address": self.object.user_email
        }

        response = requests.post(f"https://emailoctopus.com/api/1.5/lists/{list_id}/contacts", data=data)
        messages.success(self.request, 'Thanks for signing up! You should receive a confirmation email soon.')
        
        return HttpResponseRedirect(reverse_lazy('home'))

    
class ProjectCreateView(SuccessMessageMixin, CreateView):
    model = Project
    form_class = AddProject
    template_name = 'submit-project.html'
    success_url = reverse_lazy('home')
    success_message = "Thanks for submitting your project! I'll let you know when it is up on the site!"

    
