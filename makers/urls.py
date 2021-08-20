from django.urls import path
from .views import MakerListView

urlpatterns = [
    path("", MakerListView.as_view(), name="makers"),
]
