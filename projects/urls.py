from django.urls import path
from .views import ProjectListView, ProjectCreateView

urlpatterns = [
    path('', ProjectListView.as_view(), name='home'),
    path('project/new/', ProjectCreateView.as_view(), name='submit_project'),
]