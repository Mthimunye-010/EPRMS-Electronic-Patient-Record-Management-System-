from django.core.paginator import Paginator
from django.shortcuts import render

from accounts.decorators import role_required
from .models import AuditLog


@role_required("ADMIN")
def audit_log_list(request):
    logs = AuditLog.objects.select_related("user").all()

    action = request.GET.get("action")
    if action:
        logs = logs.filter(action=action)

    q = request.GET.get("q")
    if q:
        logs = logs.filter(username_snapshot__icontains=q)

    paginator = Paginator(logs, 50)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "audit/audit_log_list.html",
        {"page_obj": page_obj, "action_choices": AuditLog.Action.choices, "selected_action": action, "q": q or ""},
    )
