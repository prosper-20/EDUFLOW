from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models
from PIL import Image
from .managers import CustomUserManager
from datetime import timedelta
import random
import secrets
from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from lms.models import *


ROLE_CHOICES = (
    ("Student", "Student"),
    ("Instructor", "Instructor"),
    ("Admin", "Admin"),
)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255)
    email = models.EmailField(_("email address"), unique=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    role = models.CharField(choices=ROLE_CHOICES, max_length=50, default="Student")
    date_joined = models.DateTimeField(default=timezone.now)
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        related_name="custom_users",  # Unique related_name for CustomUser model
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        related_name="custom_users",  # Change or add related_name here
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name_plural = "Users"


class CustomToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    access_token_expires_at = models.DateTimeField()
    refresh_token_expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.id:
            # If the instance is being created (not updated), set expired_at to 30 minutes from now.
            self.access_token_expires_at = timezone.now() + timedelta(minutes=5)
            self.refresh_token_expires_at = timezone.now() + timedelta(days=1)
        super(CustomToken, self).save(*args, **kwargs)

    def is_access_token_expired(self):
        return timezone.now() >= self.access_token_expires_at

    def is_refresh_token_expired(self):
        return timezone.now() >= self.refresh_token_expires_at


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(default="user.jpg", upload_to="profile_pictures")
    faculty = models.ForeignKey(
        "lms.Faculty", on_delete=models.CASCADE, blank=True, null=True
    )
    course = models.ForeignKey(
        "lms.Course", on_delete=models.CASCADE, blank=True, null=True
    )
    level = models.ForeignKey(
        "lms.Level", on_delete=models.CASCADE, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} profile"

    class Meta:
        verbose_name_plural = "User Profiles"


class Bank(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    alias = models.CharField(max_length=100, blank=True, null=True)
    bank_code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


SUBJECT_CHOICES = (
    ("Complaint", "Complaint"),
    ("Inquiry", "Inquiry"),
    ("Others", "Others"),
)


class Contact(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    subject = models.CharField(choices=SUBJECT_CHOICES, max_length=50)
    email_address = models.EmailField()
    whatsapp_number = models.CharField(max_length=11)
    message = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name


class OTPToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otps"
    )
    otp_code = models.CharField(max_length=4)
    otp_created_at = models.DateTimeField(auto_now_add=True)
    otp_expires_at = models.DateTimeField()

    def __str__(self):
        return self.user.email

    def save(self, *args, **kwargs):
        if not self.otp_expires_at:
            self.otp_expires_at = timezone.now() + timedelta(minutes=10)
        if not self.otp_code:
            self.otp_code = "{:04d}".format(secrets.randbelow(10000))

        super(OTPToken, self).save(*args, **kwargs)


class EmailOTPToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="email_otps"
    )
    otp_code = models.CharField(max_length=4)
    otp_created_at = models.DateTimeField(auto_now_add=True)
    otp_expires_at = models.DateTimeField()

    def __str__(self):
        return self.user.email

    def save(self, *args, **kwargs):
        if not self.otp_expires_at:
            self.otp_expires_at = timezone.now() + timedelta(minutes=5)
        if not self.otp_code:
            self.otp_code = "{:04d}".format(secrets.randbelow(10000))

        super(EmailOTPToken, self).save(*args, **kwargs)
