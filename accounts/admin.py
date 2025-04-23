from django.contrib import admin
from accounts.models import CustomUser
from .models import UserProfile
from lms.models import Course, Faculty
from django.conf import settings


class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "email", "role", "is_verified"]
    list_filter = ["is_verified"]


admin.site.register(CustomUser, UserAdmin)
admin.site.register([UserProfile])
