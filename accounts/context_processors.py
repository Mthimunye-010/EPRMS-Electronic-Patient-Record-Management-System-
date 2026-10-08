from django.conf import settings


def security_context(request):
    return {
        "session_timeout_seconds": getattr(settings, "SESSION_INACTIVITY_TIMEOUT", 900),
        "account_last_login": request.user.last_login if request.user.is_authenticated else None,
    }
