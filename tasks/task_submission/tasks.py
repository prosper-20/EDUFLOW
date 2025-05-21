from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from lms.models import ClassroomAnnouncement, Classroom, TaskSubmission
from decouple import config
from django.conf import settings


@shared_task
def notify_instructor_of_submission(submission_id):
    try:
        submission = TaskSubmission.objects.get(submission_id=submission_id)
        instructor = (
            submission.task.instructor
        )  # Assuming Task model has instructor field

        subject = f"New Submission for {submission.task.task}"
        context = {
            "task_title": submission.task.task,
            "student_name": submission.student.username,
            "submission_date": submission.submitted_at,
            "submission_url": f"{settings.BASE_URL}/submissions/{submission.submission_id}/",
        }

        html_message = render_to_string(
            "emails/new_submission_notification.html", context
        )
        plain_message = strip_tags(html_message)

        send_mail(
            subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instructor.email],
            html_message=html_message,
            fail_silently=False,
        )

        return f"Email sent to {instructor.email}"
    except Exception as e:
        return f"Error sending email: {str(e)}"
