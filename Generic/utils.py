import requests
import random
import string
from django.db.models import Model
import os
from django.core.exceptions import ValidationError
from django.utils.text import slugify


def generate_class_id(self):
    """Generate a random 6-digit alphanumeric ID"""
    while True:
        # Create 6-character code with digits and uppercase letters
        code = ''.join(random.choices(
            string.ascii_uppercase + string.digits, 
            k=6
        ))
        
        # Check if code already exists
        if not self.objects.filter(class_id=code).exists():
            return code
        



def task_submission_upload_path(instance, filename):
    """
    Returns the upload path for task submission files in the format:
    task_submissions/<task_name>/<filename>
    """
    # Clean the task name to remove special characters and spaces
    task_name = slugify(instance.task.task)
    return f'task_submissions/{task_name}/{filename}'


def is_valid_file_type(file, allowed_file_types):
    """
    Check if a file's extension is in the allowed file types
    :param file: UploadedFile object
    :param allowed_file_types: QuerySet of FileType objects or list of allowed extensions
    :return: bool
    """
    if not file:
        return False
    
    # Get file extension (with or without dot based on your FileType model)
    ext = os.path.splitext(file.name)[1].lower()  # keeps the dot (e.g., ".pdf")
    ext_no_dot = ext[1:] if ext.startswith('.') else ext  # without dot
    
    # Check if allowed_file_types is a QuerySet of FileType objects
    if hasattr(allowed_file_types, 'filter'):
        # Try both with and without dot depending on how your FileType stores them
        return (allowed_file_types.filter(ext=ext).exists() or 
                allowed_file_types.filter(ext=ext_no_dot).exists())
    
    # If it's just a list of extensions
    return ext in allowed_file_types or ext_no_dot in allowed_file_types