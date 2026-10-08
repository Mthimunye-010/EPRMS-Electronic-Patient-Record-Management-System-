from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils import timezone

from patients.models import Patient
from records.models import Appointment


@login_required
def dashboard(request):
    if not request.user.is_active or not request.user.is_active_staff:
        raise PermissionDenied("Your account is inactive.")
    today = timezone.localdate()
    is_admin = request.user.role == request.user.Role.ADMIN
    User = get_user_model()
    context = {
        "is_admin": is_admin,
        "active_staff_count": User.objects.filter(is_active=True, is_active_staff=True).count() if is_admin else None,
        "total_patients": Patient.objects.filter(is_active=True).count() if not is_admin else None,
        "todays_appointments": (
            Appointment.objects.filter(date=today)
            .exclude(status="CANCELLED")
            .select_related("patient", "doctor")
            if not is_admin else Appointment.objects.none()
        ),
        "upcoming_appointments_count": (
            Appointment.objects.filter(date__gte=today, status="SCHEDULED").count()
            if not is_admin else None
        ),
    }
    return render(request, "core/dashboard.html", context)


@login_required
def privacy(request):
    return render(request, "core/privacy.html")
