from datetime import timedelta

from django.db.models import Count
from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_date

from accounts.decorators import role_required
from .models import AuditLog


@role_required("ADMIN")
def audit_log_list(request):
    logs = AuditLog.objects.select_related("user").all()

    action = request.GET.get("action", "")
    if action:
        if action in dict(AuditLog.Action.choices):
            logs = logs.filter(action=action)
        else:
            logs = logs.none()

    q = request.GET.get("q", "").strip()[:100]
    if q:
        logs = logs.filter(username_snapshot__icontains=q)

    start = parse_date(request.GET.get("start", ""))
    end = parse_date(request.GET.get("end", ""))
    if start:
        logs = logs.filter(timestamp__date__gte=start)
    if end:
        logs = logs.filter(timestamp__date__lte=end)

    paginator = Paginator(logs, 50)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "audit/audit_log_list.html",
        {
            "page_obj": page_obj,
            "action_choices": AuditLog.Action.choices,
            "selected_action": action,
            "q": q,
            "start_date": start,
            "end_date": end,
        },
    )


@role_required("ADMIN")
def security_dashboard(request):
    now = timezone.now()
    day_ago = now - timedelta(hours=24)
    hour_ago = now - timedelta(hours=1)
    failed_login_action = AuditLog.Action.LOGIN_FAILED
    denied_action = AuditLog.Action.ACCESS_DENIED
    reveal_action = AuditLog.Action.SENSITIVE_REVEAL
    security_events = AuditLog.objects.filter(
        timestamp__gte=day_ago,
        action__in=[failed_login_action, denied_action, reveal_action, AuditLog.Action.REAUTH_FAILED],
    )
    unusual_views = (
        AuditLog.objects.filter(
            action=AuditLog.Action.VIEW,
            target_model="Patient",
            timestamp__gte=hour_ago,
        )
        .values("username_snapshot")
        .annotate(view_count=Count("id"))
        .filter(view_count__gte=20)
        .order_by("-view_count")[:20]
    )
    return render(request, "audit/security_dashboard.html", {
        "failed_logins": AuditLog.objects.filter(action=failed_login_action, timestamp__gte=day_ago).count(),
        "access_denials": AuditLog.objects.filter(action=denied_action, timestamp__gte=day_ago).count(),
        "sensitive_reveals": AuditLog.objects.filter(action=reveal_action, timestamp__gte=day_ago).count(),
        "unusual_views": unusual_views,
        "security_events": security_events.select_related("user")[:50],
    })
