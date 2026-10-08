from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.conf import settings
from django.utils import timezone


class CurrentUserMiddleware:
    """Keeps the current request available to audit helpers."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request._audit_request = True
        return self.get_response(request)


class InactivityTimeoutMiddleware:
    """Log out authenticated users after the configured inactivity period."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if not request.user.is_active or not request.user.is_active_staff:
                logout(request)
                messages.warning(request, "Your hospital account is no longer active. Please contact an administrator.")
                return redirect("accounts:login")
            now = timezone.now().timestamp()
            last_activity = request.session.get("last_activity")
            timeout = getattr(settings, "SESSION_INACTIVITY_TIMEOUT", 900)
            if last_activity and now - float(last_activity) > timeout:
                logout(request)
                messages.warning(request, "You were logged out because of inactivity.")
                return redirect("accounts:login")
            request.session["last_activity"] = now
        return self.get_response(request)
