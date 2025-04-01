from django.contrib import admin
from django.contrib.auth import get_user_model
# from .models import UserProfile
# from lms.models import Course, Faculty


User = get_user_model()

class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "email", "role", "is_verified"]
    list_filter = ["is_verified"]

admin.site.register(User, UserAdmin)
# admin.site.register([Course, Faculty, UserProfile])
