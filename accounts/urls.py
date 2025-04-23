from django.urls import path
from .views import (
    UserCreationView,
    InstructorCreationView,
    LoginAPIView,
    UserProfileAPIView,
)


urlpatterns = [
    path("create/", UserCreationView.as_view(), name="create-account"),
    path(
        "create/instructor/",
        InstructorCreationView.as_view(),
        name="create-instructor-account",
    ),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("profile/", UserProfileAPIView.as_view(), name="user-profile"),
]
