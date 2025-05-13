from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile, Faculty, Course, Department, CustomUser
from django.contrib.auth import authenticate
from tasks.lms.accounts.welcome_mail import send_welcome_email

User = get_user_model()


class UserCreationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "role", "password", "password2"]
        extra_kwargs = {"password": {"write_only": True}, "role": {"required": False}}

    def validate_password(self, value):
        min_length = 8
        if len(value) < min_length:
            raise serializers.ValidationError(
                f"Password must be at least {min_length} characters long."
            )

        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one digit."
            )

        return value

    def save(self):
        user = User(
            username=self.validated_data.get("username"),
            email=self.validated_data.get("email"),
        )
        password = self.validated_data["password"]
        password2 = self.validated_data["password2"]

        if password != password2:
            raise serializers.ValidationError({"Error": "Both passwords must match"})
        user.set_password(password)
        user.save()

        
        send_welcome_email.delay(user.id)
        return user


class InstructorCreationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)
    faculty = serializers.CharField(required=True, max_length=30)
    department = serializers.CharField(required=True, max_length=70)

    class Meta:
        model = User
        fields = ["username", "email", "faculty", "department", "password", "password2"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_faculty(self, value):
        try:
            faculty = Faculty.objects.get(name=value)
        except Faculty.DoesNotExist:
            raise serializers.ValidationError(
                f"Faculty with name {value} does not exist"
            )
        return value

    def validate_department(self, value):
        try:
            department = Department.objects.get(name=value)
        except Department.DoesNotExist:
            raise serializers.ValidationError(
                f"Department with name {value} does not exist"
            )
        return value

    def validate_password(self, value):
        min_length = 8
        if len(value) < min_length:
            raise serializers.ValidationError(
                f"Password must be at least {min_length} characters long."
            )

        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one digit."
            )

        return value

    def save(self):
        user = User(
            username=self.validated_data.get("username"),
            email=self.validated_data.get("email"),
        )
        password = self.validated_data["password"]
        password2 = self.validated_data["password2"]

        user_faculty = Faculty.objects.get(
            name__iexact=self.validated_data.get("faculty")
        )

        if password != password2:
            raise serializers.ValidationError({"Error": "Both passwords must match"})
        user.set_password(password)
        user.role = "Instructor"
        user.save()
        user_profile = UserProfile.objects.get(user=user)
        user_profile.faculty = user_faculty
        user_profile.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    # def validate_email(self, value):
    #     if value.get("email") and value.get("password"):
    #         if CustomUser.objects.filter(email=value).exists():
    #             return value
    #         raise serializers.ValidationError("Email address not found")

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(email=email, password=password)

            if user:
                if not user.is_active:
                    msg = "User account is disabled."
                    raise serializers.ValidationError(msg, code="authorization")
            else:
                msg = "Unable to log in with provided credentials."
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code="authorization")

        data["user"] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField("get_user_data")

    class Meta:
        model = UserProfile
        fields = "__all__"

    def get_user_data(self, obj: UserProfile):
        return obj.user.username, obj.user.email


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "email"]


class EditUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["image", "course"]


class InitiatePasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            return value
        raise serializers.ValidationError("Email address does not exist.")


class PasswordChangeSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=100, required=True)
    confirm_new_password = serializers.CharField(max_length=100, required=True)

    def validate(self, data):
        new_password = data.get("new_password")
        confirm_new_password = data.get("confirm_new_password")

        if new_password != confirm_new_password:
            raise serializers.ValidationError(
                "The new password and its confirmation do not match."
            )

        return data


class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        max_length=20, style={"input_type": "password"}, write_only=True
    )
    confirm_new_password = serializers.CharField(
        max_length=20, style={"input_type": "password"}, write_only=True
    )

    def validate_passwords(self, value):
        if self.new_password != self.confirm_new_password:
            raise serializers.ValidationError({"Response": "Both passwords must match"})
