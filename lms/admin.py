from django.contrib import admin
from .models import Faculty, Department, Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["name", "faculty", "department", "code"]
    list_filter = ["department", "faculty"]
    search_fields = ["name", "code"]


admin.site.register([Faculty, Department])