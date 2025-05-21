from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TaskSubmission
from tasks.task_submission.tasks import notify_instructor_of_submission


@receiver(post_save, sender=TaskSubmission)
def handle_new_submission(sender, instance, created, **kwargs):
    if created:  # Only for new, non-draft submissions
        notify_instructor_of_submission.delay(instance.id)
