from django.db import models
from django.conf import settings
from listings.models import Listing

class Inquiry(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_inquiries')
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_inquiries')

    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('new', 'New'),
            ('in_chat', 'In Chat'),
            ('accepted', 'Accepted'),
            ('declined', 'Declined')
        ],
        default='new'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inquiry for {self.listing.title} from {self.from_user.email}"

class ChatMessage(models.Model):
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read_flag = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.email}"
