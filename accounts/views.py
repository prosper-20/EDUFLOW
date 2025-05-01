from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from lms.serializers.courses.serializers import CourseSerializer
from accounts.serializers import (
    UserCreationSerializer,
    InstructorCreationSerializer,
    LoginSerializer,
    UserProfileSerializer,
    EditUserProfileSerializer,
    InitiatePasswordResetSerializer,
    PasswordResetSerializer,
    PasswordChangeSerializer
)
from .models import CustomToken, UserProfile
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from lms.models import Course
from Generic.lms.permissions import IsStudent
from django.core.mail import send_mail
from decouple import config
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_str
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str


User = get_user_model()


class UserCreationView(APIView):
    def post(self, request):
        serializer = UserCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        message = {"Success": "Account Creation Successful!", "Data": serializer.data}
        return Response(message, status=status.HTTP_201_CREATED)


class InstructorCreationView(APIView):
    def post(self, request):
        serializer = InstructorCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        message = {
            "Success": "Instructor Creation Successful!",
            "Data": serializer.data,
        }
        return Response(message, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            user = User.objects.get(email=email)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                access_token = AccessToken.for_user(user)

                # Store tokens in CustomToken model
                custom_token, _ = CustomToken.objects.get_or_create(user=user)
                custom_token.access_token = str(access_token)
                custom_token.refresh_token = str(refresh)
                custom_token.access_token_expires_at = timezone.now() + timedelta(
                    minutes=120
                )
                # print(timezone.now(), str(custom_token.access_token_expires_at))
                custom_token.refresh_token_expires_at = timezone.now() + timedelta(
                    days=1
                )
                custom_token.save()

                return Response(
                    {
                        "role": user.role,
                        "access_token": str(access_token),
                        "refresh_token": str(refresh),
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = get_object_or_404(UserProfile, user=user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        profile = get_object_or_404(UserProfile, user=user)
        serializer = EditUserProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"Success": "Profile update successful", "data": serializer.data},
            status=status.HTTP_202_ACCEPTED,
        )
    


class ListUserFavouriteCoursesAPIView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        user = request.user
        courses = Course.objects.filter(favourite_courses__user=request.user)
        favourite_count = user.userprofile.favourite_courses.count()
        serializer = CourseSerializer(courses, many=True)
        return Response({"Count": favourite_count,
                         "data":serializer.data}, status=status.HTTP_200_OK)
    




class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None, **kwargs):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        current_user = User.objects.get(email=request.user)
        # if not current_user.check_password(serializer.validated_data['old_password']):
        #     return Response({"Error": "Current password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.is_valid(raise_exception=True)
        current_user.set_password(serializer.validated_data['new_password'])
        current_user.save()
        return Response({"Success": "Password successfully changed"}, status=status.HTTP_202_ACCEPTED)



class InitiatePasswordResetView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, format=None):
        serializer = InitiatePasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = get_object_or_404(User, email=email)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"http://127.0.0.1:8000/accounts/reset-password/{uid}/{token}/"
        
        subject = 'Password Reset!'
        html_message = render_to_string('accounts/password_reset_email.html', {'uid': uid, 'token': token, 'reset_link': reset_link})
        plain_message = strip_tags(html_message)
        from_email = config('DEFAULT_FROM_EMAIL')  # Replace with your email
        to = email
        send_mail(subject, plain_message, from_email, [to], html_message=html_message)
        return Response({"Success": "Password Reset email sent!"}, status=status.HTTP_200_OK)




class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token, format=None):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            new_password = serializer.validated_data.get('new_password')
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid reset link'}, status=status.HTTP_400_BAD_REQUEST)
