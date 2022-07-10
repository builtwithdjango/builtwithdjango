from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView
from django_q.tasks import async_task

from newsletter.forms import NewsletterSignupForm

from .forms import CreateCommentForm
from .models import Comment, Post
from .tasks import notify_admin_of_guide_comment


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
        context["comment_form"] = CreateCommentForm

        return context


class CommentCreateView(CreateView):
    model = Comment
    form_class = CreateCommentForm
    template_name = "blog/create-guide-comment.html"

    def get_success_url(self):
        return reverse("post", kwargs={"slug": self.object.post.slug})

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = Post.objects.get(slug=self.kwargs["slug"])
        self.object = form.save()
        async_task(notify_admin_of_guide_comment, self.object)

        return super(CommentCreateView, self).form_valid(form)
