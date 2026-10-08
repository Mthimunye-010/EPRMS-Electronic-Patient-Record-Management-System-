from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class StaffUserAdmin(UserAdmin):
    list_display = ("username", "first_name", "last_name", "role", "employee_id", "is_active_staff", "is_active")
    list_filter = ("role", "is_active_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("Hospital staff details", {"fields": ("role", "employee_id", "department", "phone_number", "is_active_staff")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Hospital staff details", {"fields": ("role", "employee_id", "department", "phone_number")}),
    )
