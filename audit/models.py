from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """
    Records important user activities across the system, as required by the
    project's security objectives (Section 3.3) and success criteria
    (Section 7.2): "Record important user activities through audit logs."
    """

    class Action(models.TextChoices):
        LOGIN = "LOGIN", "Login"
        LOGOUT = "LOGOUT", "Logout"
        CREATE = "CREATE", "Create"
        UPDATE = "UPDATE", "Update"
        DELETE = "DELETE", "Delete"
        SEARCH = "SEARCH", "Search"
        VIEW = "VIEW", "View"
        DUPLICATE_FLAG = "DUPLICATE_FLAG", "Potential duplicate flagged"
        BACKUP = "BACKUP", "Database backup"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs"
    )
    username_snapshot = models.CharField(
        max_length=150, blank=True, help_text="Username at time of action, kept even if the user is later deleted."
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    target_model = models.CharField(max_length=100, blank=True)
    target_id = models.CharField(max_length=50, blank=True)
    target_repr = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Audit log entry"
        verbose_name_plural = "Audit log entries"

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.username_snapshot} - {self.get_action_display()} {self.target_repr}"
