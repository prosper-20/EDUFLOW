from django.contrib import admin
from .models import (
    Faculty,
    Department,
    Course,
    Enrollment,
    Module,
    Content,
    Task,
    FileType,
    Classroom,
    Level,
    TaskSubmission,
    ClassroomAnnouncement,
    Comment,
    Question,
    Option,
    Quiz,
    QuizQuestion,
)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ["course", "title"]


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ("question", "text", "is_correct")
    list_filter = ("is_correct",)
    search_fields = ("option_text",)
    list_editable = ["is_correct"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["id", "course"]
    search_fields = ["text"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["content", "author", "text", "created_at", "is_active"]
    list_editable = ["is_active"]
    list_filter = ["author", "content"]


@admin.register(TaskSubmission)
class TaskSubmissionAdmin(admin.ModelAdmin):
    list_display = ["submission_id", "task", "student", "file_upload"]
    list_filter = ["task"]
    search_fields = ["student"]
    readonly_fields = ("submission_id",)


admin.site.register(Level)


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ["class_id", "name", "owner"]
    list_filter = ["owner"]
    search_fields = ["name", "class_id"]


@admin.register(FileType)
class FileTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "ext")


class ModuleInline(admin.StackedInline):
    model = Module


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["name", "faculty", "department", "code"]
    list_filter = ["department", "faculty"]
    search_fields = ["name", "code"]
    inlines = [ModuleInline]


admin.site.register([Faculty, Department, Enrollment, Module, ClassroomAnnouncement])


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ["content_id", "module", "content_type"]
    list_filter = ["module", "content_type"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["task_id", "module", "task_type", "available_until"]
    list_filter = ["module", "task_type", "available_until"]
    search_fields = ["module", "task_type", "available_until"]
    date_hierarchy = "available_from"
    actions = ["mark_as_overdue"]
    readonly_fields = ("task_id",)

    def mark_as_overdue(self, request, queryset):
        queryset.update(is_overdue=True)
