from django.db import models
from django.conf import settings
from listings.models import Listing
from django.utils import timezone
import os

def agreement_upload_to(instance, filename):
    # e.g. agreements/listing-12/agreement-<timestamp>.pdf
    base = f"agreements/listing-{instance.listing.id}"
    name = f"agreement-{int(timezone.now().timestamp())}.pdf"
    return os.path.join(base, name)

class Agreement(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='agreements')
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tenant_agreements')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owner_agreements')

    # Data fields submitted by the users (can be expanded)
    rent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deposit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    clauses = models.TextField(blank=True)

    # Track who has submitted consent/details
    tenant_submitted = models.BooleanField(default=False)
    owner_submitted = models.BooleanField(default=False)

    # generated pdf file
    pdf_file = models.FileField(upload_to=agreement_upload_to, null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[('draft','Draft'), ('awaiting_signatures','Awaiting Signatures'),
                 ('completed','Completed')],
        default='draft'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def both_submitted(self):
        return self.tenant_submitted and self.owner_submitted

    def __str__(self):
        return f"Agreement for {self.listing.title} ({self.pk})"
