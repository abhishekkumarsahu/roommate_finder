from django.contrib import admin
from .models import Listing, ListingImage
from common.utils import notify

class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'rent', 'status')
    list_filter = ('status',)
    inlines = [ListingImageInline]

    actions = ['approve_listings', 'reject_listings']

    def approve_listings(self, request, queryset):
        for listing in queryset:
            listing.status = 'approved'
            listing.save()

            # 🔔 SEND APPROVAL NOTIFICATION
            notify(
                user=listing.owner,
                message=f"Your listing '{listing.title}' has been approved!",
                link=f"/listings/{listing.id}/"
            )

        self.message_user(request, "Selected listings approved.")
    approve_listings.short_description = "Approve selected listings"

    def reject_listings(self, request, queryset):
        for listing in queryset:
            listing.status = 'rejected'
            listing.save()

            # 🔔 SEND REJECTION NOTIFICATION
            notify(
                user=listing.owner,
                message=f"Your listing '{listing.title}' has been rejected.",
                link=f"/listings/{listing.id}/"
            )

        self.message_user(request, "Selected listings rejected.")
    reject_listings.short_description = "Reject selected listings"
