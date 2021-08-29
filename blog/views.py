from django.views.generic import DetailView, ListView

from newsletter.forms import NewsletterSignupForm

from .models import Post


class PostListView(ListView):
    model = Post
    template_name = "blog/all_posts.html"
    queryset = Post.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context
