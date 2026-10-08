from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django_otp.admin import OTPAdminSite

from .models import User


class EPRMSOTPAdminSite(OTPAdminSite):
    def has_permission(self, request):
        return super().has_permission(request) and request.user.is_active_staff


otp_admin_site = EPRMSOTPAdminSite(name="otp_admin")

@admin.register(User, site=otp_admin_site)
class StaffUserAdmin(UserAdmin):
    list_display = ("username", "first_name", "last_name", "role", "employee_id", "is_active_staff", "is_active")
    list_filter = ("role", "is_active_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("Hospital staff details", {"fields": ("role", "employee_id", "department", "phone_number", "is_active_staff")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Hospital staff details", {"fields": ("role", "employee_id", "department", "phone_number")}),
    )
