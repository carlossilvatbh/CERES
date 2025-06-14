from django.contrib import admin

from .models import EnrollmentSession


@admin.register(EnrollmentSession)
class EnrollmentSessionAdmin(admin.ModelAdmin):
    list_display = ("customer", "status", "current_step", "completion_percentage", "last_activity_at")
    search_fields = ("customer__id", "resume_token")
