from django.db import models
from django.conf import settings

class Listing(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    description = models.TextField()

    rent = models.DecimalField(max_digits=10, decimal_places=2)
    deposit = models.DecimalField(max_digits=10, decimal_places=2)

    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    available_from = models.DateField()

    # Tenant Preferences
    preferred_gender = models.CharField(
        max_length=20,
        choices=[('any', 'Any'), ('male', 'Male'), ('female', 'Female')]
    )
    preferred_occupation = models.CharField(max_length=50, blank=True, null=True)

    amenities = models.JSONField(default=list)  # e.g. ["wifi", "parking"]

    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('occupied', 'Occupied')],
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='listing_images/')
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.listing.title}"
