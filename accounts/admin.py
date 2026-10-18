from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "student_code", "phone")
    search_fields = ("user__username", "user__email", "student_code")
