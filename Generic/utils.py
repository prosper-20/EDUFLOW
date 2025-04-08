import requests
import random
import string
from django.db.models import Model

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