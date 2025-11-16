from .models import Notification
from django.core.mail import send_mail
from django.conf import settings

def notify(user, message, link=None):
    # DB notification
    Notification.objects.create(
        user=user,
        message=message,
        link=link
    )

    # Email notification
    try:
        send_mail(
            subject="Roommate Finder Notification",
            message=f"{message}\n\nOpen: {link if link else ''}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True
        )
    except:
        pass
