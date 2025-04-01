from django.urls import path
from .views import CreateCourseAPIView, RetrieveCourseAPIView


urlpatterns = [
    path("courses/create/", CreateCourseAPIView.as_view(), name="create-course"),
    path("courses/<str:slug>/", RetrieveCourseAPIView.as_view(), name="retrieve-course"),
]