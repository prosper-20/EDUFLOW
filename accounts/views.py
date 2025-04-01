from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from accounts.serializers import UserCreationSerializer, InstructorCreationSerializer, LoginSerializer
from .models import CustomToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken


User = get_user_model()

class UserCreationView(APIView):
    def post(self, request):
        serializer = UserCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        message = {"Success": "Account Creation Successful!",
                   "Data": serializer.data}
        return Response(message, status=status.HTTP_201_CREATED)
    



class InstructorCreationView(APIView):
    def post(self, request):
        serializer = InstructorCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        message = {"Success": "Instructor Creation Successful!",
                   "Data": serializer.data}
        return Response(message, status=status.HTTP_201_CREATED)
    


class LoginAPIView(APIView):
    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        data = {}
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                access_token = AccessToken.for_user(user)

                # Store tokens in CustomToken model
                custom_token, _ = CustomToken.objects.get_or_create(user=user)
                custom_token.access_token = str(access_token)
                custom_token.refresh_token = str(refresh)
                custom_token.access_token_expires_at = timezone.now() + timedelta(minutes=120)
                # print(timezone.now(), str(custom_token.access_token_expires_at))
                custom_token.refresh_token_expires_at = timezone.now() + timedelta(days=1)
                custom_token.save()

                return Response({
                    "role": user.role,
                    'access_token': str(access_token),
                    'refresh_token': str(refresh)
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
