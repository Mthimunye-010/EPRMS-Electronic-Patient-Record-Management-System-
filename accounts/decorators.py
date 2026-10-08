from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from audit.models import AuditLog
from audit.utils import log_action


def role_required(*allowed_roles):
    """Allow only authenticated, active staff members with an allowed role."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_active or not user.is_active_staff:
                raise PermissionDenied("Your account is inactive.")
            if user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            log_action(
                request,
                action=AuditLog.Action.ACCESS_DENIED,
                description=f"Denied {request.method} access to {request.path}.",
            )
            messages.error(request, "You do not have permission to access that page.")
            raise PermissionDenied("Insufficient role for this action.")
        return _wrapped
    return decorator


class RoleRequiredMixin:
    allowed_roles = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        if not request.user.is_active or not request.user.is_active_staff:
            raise PermissionDenied("Your account is inactive.")
        if request.user.role not in self.allowed_roles:
            log_action(
                request,
                action=AuditLog.Action.ACCESS_DENIED,
                description=f"Denied {request.method} access to {request.path}.",
            )
            messages.error(request, "You do not have permission to access that page.")
            raise PermissionDenied("Insufficient role for this action.")
        return super().dispatch(request, *args, **kwargs)
