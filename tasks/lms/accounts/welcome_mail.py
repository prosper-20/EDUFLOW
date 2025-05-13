from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task
def send_welcome_email(user_id):
      # Import inside function to avoid circular imports
    
    try:
        user = User.objects.get(id=user_id)
        
        subject = "Welcome to Our Platform!"
        
        # Prepare email content
        context = {
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'support_email': settings.DEFAULT_FROM_EMAIL,
        }
        
        html_message = render_to_string('emails/welcome_email.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,  # Uses DEFAULT_FROM_EMAIL from settings
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return f"Welcome email sent to {user.email}"
    
    except User.DoesNotExist:
        return "User not found"