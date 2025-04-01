from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings

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
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={"role": "Instructor"})
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
