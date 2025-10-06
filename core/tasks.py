from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import Goal
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_reminder_emails():
    logger.info("Starting reminder task")
    seven_days_ago = timezone.now() - timedelta(days=7)
    goals = Goal.objects.filter(
        last_progress_date__lt=seven_days_ago,
        last_reminder_sent_at__isnull=True
    ).select_related('user')
    logger.info(f"Found {goals.count()} inactive goals")
    for goal in goals:
        user = goal.user
        logger.info(f"Sending reminder for goal {goal.id} to {user.email}")
        send_mail(
            subject='Remainder:Update your goal progress',
            message=f"Hi {user.username}, you haven't updated your {goal} in over 7 days!",
            from_email="randomdude@learnflow.com",
            recipient_list=[user.email],
            fail_silently=False,  
        )
        logger.info(f"Email sent to {user.email}")
        goal.last_reminder_sent_at = timezone.now()
        goal.save()
    logger.info("Reminder task completed")