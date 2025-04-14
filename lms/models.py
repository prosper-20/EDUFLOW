from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from .fields import OrderField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from Generic.utils import generate_class_id, task_submission_upload_path
import uuid
import random
import string

# User = get_user_model()

class Faculty(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Faculties"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Department(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Departments"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
   
    

class Course(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(blank=True, null=True)
    code = models.CharField(max_length=10, blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={"role__in": ["Instructor", "Admin"]})
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)





class Enrollment(models.Model):
    ENROLLMENT_STATUS = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
        ('withdrawn', 'Withdrawn'),
    )

    GRADE_CHOICES = (
        ('A', 'Excellent'),
        ('B', 'Good'),
        ('C', 'Average'),
        ('D', 'Below Average'),
        ('F', 'Fail'),
    )

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments', limit_choices_to={'role': 'Student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ENROLLMENT_STATUS, default='active')
    grade = models.CharField(max_length=2,blank=True, null=True, choices=GRADE_CHOICES)
    score = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    is_audit = models.BooleanField(default=False)
    completion_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # unique_together = ['student', 'course']
        ordering = ['-enrollment_date']
        verbose_name_plural = "Enrollments"

    def __str__(self):
        return f"{self.student} in {self.course}"

    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.completion_date:
            self.completion_date = timezone.now()
        super().save(*args, **kwargs)





class ItemBase(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_related', on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
    
    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=['course'])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.order}. {self.title}'


class Content(models.Model):
    module = models.ForeignKey(Module,related_name='contents', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'model__in':(
                                     'text',
                                     'video',
                                     'image',
                                     'file')})
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']


class ItemBase(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              related_name='%(class)s_related',
                              on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class Text(ItemBase):
    content = models.TextField()


class File(ItemBase):
    file = models.FileField(upload_to='files')


class Image(ItemBase):
    file = models.FileField(upload_to='images')


class Video(ItemBase):
    url = models.URLField()

from django.utils import timezone

class FileType(models.Model):
    name = models.CharField(max_length=10)
    ext = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Task(models.Model):
    """
    Represents an assignment within a course module
    """
    TASK_TYPES = (
        ('assignment', 'assignment'),
        ('quiz assignment', 'quiz assignment'),
        ('question', 'question'),
    
    )
    
    SUBMISSION_TYPES = (
        ('file', 'File Upload'),
        ('text', 'Text Entry'),
        ('url', 'URL Submission'),
        ('none', 'No Submission'),
    )

    task_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    task_type = models.CharField(max_length=20, choices=TASK_TYPES)
    task = models.TextField()
    slug = models.SlugField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='assignments')
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={"role": "Instructor"}, related_name='created_assignments')
    task_file = models.FileField(upload_to="tasks/files/", blank=True, null=True)
    # Assignment configuration
    
    submission_type = models.CharField(max_length=20, choices=SUBMISSION_TYPES, default='file')
    allowed_file_types = models.ManyToManyField(FileType, blank=True, help_text="Select all allowed file extensions (e.g., pdf,docx)")
    max_file_size = models.PositiveIntegerField(default=10, help_text="Maximum file size in MB")
    
    # Grading
    total_points = models.PositiveIntegerField(default=100)
    grading_rubric = models.TextField(blank=True)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField()
    available_from = models.DateTimeField(default=timezone.now)
    available_until = models.DateTimeField(blank=True, null=True)
    
    # Settings
    is_published = models.BooleanField(default=False)
    allow_late_submissions = models.BooleanField(default=False)
    late_submission_penalty = models.FloatField(default=0.0, 
                                              help_text="Percentage penalty per day (e.g., 5.0 for 5% per day)")
    require_passing_score = models.BooleanField(default=False)
    passing_score = models.PositiveIntegerField(default=70, 
                                              help_text="Minimum score needed to pass (if required)")
    
    # Discussion
    allow_discussion = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['due_date']
    
    def __str__(self):
        return f"{self.task} - {self.course.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.task)
        return super().save(*args, **kwargs)

class TaskSubmission(models.Model):
    """
    Represents a student's submission for an assignment
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={"role":"Student"}, related_name='assignment_submissions')
    
    # Submission content
    submission_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    text_content = models.TextField(blank=True)
    file_upload = models.FileField(upload_to=task_submission_upload_path, blank=True, null=True)
    url_submission = models.URLField(blank=True)
    
    # Submission metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    is_draft = models.BooleanField(default=True)
    is_late = models.BooleanField(default=False)
    
    # Grading
    grade = models.FloatField(blank=True, null=True)
    is_graded = models.BooleanField(default=False)
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, limit_choices_to={"role": "Instructor"},
                                related_name='graded_submissions')
    graded_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ('task', 'student')
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.student.username}'s submission for {self.task.task}"

class TaskAttachment(models.Model):
    """
    Additional files attached to assignments by instructors
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='assignments/attachments/')
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Attachment for {self.task.title}"

class StudentTaskProgress(models.Model):
    """
    Tracks student progress and interaction with assignments
    """
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assignment_progress')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='student_progress')
    viewed = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(blank=True, null=True)
    last_accessed = models.DateTimeField(blank=True, null=True)
    time_spent = models.PositiveIntegerField(default=0, help_text="Time spent in seconds")
    
    class Meta:
        unique_together = ('student', 'task')
        verbose_name_plural = 'Student assignment progress'
    
    def __str__(self):
        return f"{self.student.username}'s progress on {self.task.title}"
    

LEVEL_CHOICES = (
    ("100", "100 L"),
    ("200", "200 L"),
    ("300", "300 L"),
    ("400", "400 L"),
    ("500", "500 L")
)


class Level(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=10)
    
    def __str__(self):
        return self.name



class Classroom(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, limit_choices_to={"role__in": ["Instructor", "Admin"]}, on_delete=models.CASCADE, related_name="classroom_owner")
    class_id = models.CharField(max_length=6, blank=True, null=True, unique=True)
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(blank=True, null=True, unique=True)
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, limit_choices_to={"role": "Student"})
    level_restriction = models.BooleanField(default=False)
    accepted_levels = models.ManyToManyField(Level, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


    @classmethod
    def generate_class_id(cls):
        """Generate a random 6-digit alphanumeric ID"""
        while True:
            code = ''.join(random.choices(
                string.ascii_uppercase + string.digits, 
                k=6
            ))
            if not cls.objects.filter(class_id=code).exists():
                return code
    
    

    def save(self, *args, **kwargs):
        if not self.slug and not self.class_id:
            self.slug = slugify(self.name)
            self.class_id = self.__class__.generate_class_id()
        return super().save(*args, **kwargs)
    

class ClassroomAnnouncement(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    content = models.TextField()
    file = models.FileField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.classroom.name
    
    class Meta:
        verbose_name_plural = "Classroom Announcements"

    

  
    