from django.urls import path
from .views import CreateCourseAPIView, RetrieveCourseAPIView, CreateEnrollmentAPIView


urlpatterns = [
    path("courses/create/", CreateCourseAPIView.as_view(), name="create-course"),
    path("courses/<str:slug>/", RetrieveCourseAPIView.as_view(), name="retrieve-course"),
    path("courses/<str:slug>/enroll/", CreateEnrollmentAPIView.as_view(), name="create-course-enrollment"),
]