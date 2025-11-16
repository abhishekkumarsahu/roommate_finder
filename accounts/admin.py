from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'is_verified', 'verification_status')
    list_filter = ('verification_status', 'is_verified')
    actions = ['mark_verified', 'mark_rejected']

    def mark_verified(self, request, queryset):
        queryset.update(is_verified=True, verification_status='verified')
    mark_verified.short_description = 'Mark selected users as Verified'

    def mark_rejected(self, request, queryset):
        queryset.update(is_verified=False, verification_status='rejected')
    mark_rejected.short_description = 'Mark selected users as Rejected'
