from django.contrib import admin
from .models import Faculty, Department, Course, Enrollment, Module, Content, Task, FileType, Classroom, Level, TaskSubmission

@admin.register(TaskSubmission)
class TaskSubmissionAdmin(admin.ModelAdmin):
    list_display = ["task", "student", "file_upload"]
    list_filter = ["task"]
    search_fields = ["student"]

admin.site.register(Level)

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ['class_id', 'name', 'owner']
    list_filter = ['owner']
    search_fields = ["name", "class_id"]


@admin.register(FileType)
class FileTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'ext')


class ModuleInline(admin.StackedInline):
    model = Module

    
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["name", "faculty", "department", "code"]
    list_filter = ["department", "faculty"]
    search_fields = ["name", "code"]
    inlines = [ModuleInline]


admin.site.register([Faculty, Department, Enrollment, Module])


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ["module", "content_type"]
    list_filter = ["module", "content_type"]



@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["task_id", "module", "task_type", "available_until"]
    list_filter = ["module", "task_type", "available_until"]
    search_fields = ["module", "task_type", "available_until"]
    date_hierarchy = 'available_from'
    actions = ['mark_as_overdue']
    readonly_fields = ('task_id',)
    
    def mark_as_overdue(self, request, queryset):
        queryset.update(is_overdue=True)





    