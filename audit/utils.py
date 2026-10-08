from .models import AuditLog


def _client_ip(request):
    if request is None:
        return None
    # Do not blindly trust X-Forwarded-For unless a trusted proxy is configured.
    return request.META.get("REMOTE_ADDR")


def log_action(request, action, target=None, description=""):
    user = getattr(request, "user", None)
    if user is not None and not user.is_authenticated:
        user = None
    AuditLog.objects.create(
        user=user,
        username_snapshot=(user.username if user else "system"),
        action=action,
        target_model=target.__class__.__name__ if target is not None else "",
        target_id=str(getattr(target, "pk", "")) if target is not None else "",
        # Deliberately do not store __str__ representations because they may contain patient names.
        target_repr="",
        description=description,
        ip_address=_client_ip(request),
    )
