from django.urls import path
from .views import (
    UserCreationView,
    InstructorCreationView,
    LoginAPIView,
    UserProfileAPIView,
    ListUserFavouriteCoursesAPIView,
    InitiatePasswordResetView,
    PasswordChangeView,
    PasswordResetConfirmView,
)
from django.urls import include


urlpatterns = [
    path("create/", UserCreationView.as_view(), name="create-account"),
    path(
        "create/instructor/",
        InstructorCreationView.as_view(),
        name="create-instructor-account",
    ),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("profile/", UserProfileAPIView.as_view(), name="user-profile"),
    path(
        "favourites/", ListUserFavouriteCoursesAPIView.as_view(), name="user-favourites"
    ),
    path("password/reset/", InitiatePasswordResetView.as_view(), name="password-reset"),
    path("password/change/", PasswordChangeView.as_view(), name="password-change"),
    path(
        "reset-password/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path('socials/', include('drf_social_oauth2.urls', namespace='drf'))
    # path('confirm-email/<uidb64>/<str:token>/', ConfirmEmailView.as_view(), name='confirm-email'),
]
