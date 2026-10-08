from django.contrib import admin

from accounts.admin import otp_admin_site
from .models import AuditLog


@admin.register(AuditLog, site=otp_admin_site)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "username_snapshot", "action", "target_model", "target_repr")
    list_filter = ("action", "target_model")
    search_fields = ("username_snapshot", "target_repr", "description")
    readonly_fields = [f.name for f in AuditLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
