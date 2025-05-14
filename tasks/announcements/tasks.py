from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from lms.models import ClassroomAnnouncement, Classroom
from decouple import config

@shared_task
def send_announcement_email(announcement_id):
    try:
        announcement = ClassroomAnnouncement.objects.get(id=announcement_id)
        classroom = announcement.classroom
        students = classroom.students.all()
        
        subject = f"New Announcement in {classroom.name}"
        
        # Prepare email content
        context = {
            'classroom': classroom,
            'announcement': announcement,
        }
        html_message = render_to_string('accounts/announcement_notification.html', context)
        plain_message = strip_tags(html_message)
        
        # Send to each student
        for student in students:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=config("DEFAULT_FROM_EMAIL"),  # Will use DEFAULT_FROM_EMAIL from settings
                recipient_list=[student.email],
                html_message=html_message,
                fail_silently=False,
            )
            
        return f"Emails sent to {students.count()} students in {classroom.name}"
    
    except ClassroomAnnouncement.DoesNotExist:
        return "Announcement not found"