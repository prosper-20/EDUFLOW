from django.contrib import admin
from .models import Faculty, Department, Course, Enrollment, Module

class ModuleInline(admin.StackedInline):
    model = Module

    
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["name", "faculty", "department", "code"]
    list_filter = ["department", "faculty"]
    search_fields = ["name", "code"]
    inlines = [ModuleInline]


admin.site.register([Faculty, Department, Enrollment])







    