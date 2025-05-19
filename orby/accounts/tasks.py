from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings

@shared_task
def send_meeting_reminder_email(meeting_id):
    from .models import Meeting  # Import here to avoid circular imports

    print(f"[Celery Task] Starting task to send reminder for meeting ID: {meeting_id}")

    try:
        meeting = Meeting.objects.get(id=meeting_id)
        user_email = meeting.user.email
        print(f"[Celery Task] Found meeting '{meeting.title}' for user {meeting.user.full_name} ({user_email})")

        # Prepare the email content
        subject = f"Reminder: Your meeting '{meeting.title}' starts soon"
        message = f"""
        Dear {meeting.user.full_name or meeting.user.email},


        This is a reminder that your meeting "{meeting.title}" is scheduled 
        (at {meeting.start_time.strftime('%H:%M')} on {meeting.start_time.strftime('%Y-%m-%d')}).

        Meeting details:
        {meeting.description}

        Duration: {meeting.start_time.strftime('%H:%M')} - {meeting.end_time.strftime('%H:%M')}

        Best regards,
        Your Personal Assistant
        """

        # Send the email
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )

        print(f"[Celery Task] Email successfully sent to {user_email}")
        return f"Reminder sent to {user_email} for meeting {meeting.title}"

    except Meeting.DoesNotExist:
        print(f"[Celery Task] Meeting with ID {meeting_id} not found")
        return f"Meeting with ID {meeting_id} not found"

    except Exception as e:
        print(f"[Celery Task] Error sending reminder: {str(e)}")
        return f"Error sending reminder: {str(e)}"
