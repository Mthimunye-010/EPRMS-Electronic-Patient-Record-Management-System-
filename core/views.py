from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from patients.models import Patient
from records.models import Appointment


@login_required
def dashboard(request):
    today = timezone.localdate()
    context = {
        "total_patients": Patient.objects.filter(is_active=True).count(),
        "todays_appointments": Appointment.objects.filter(date=today).exclude(status="CANCELLED").select_related("patient", "doctor"),
        "upcoming_appointments_count": Appointment.objects.filter(date__gte=today, status="SCHEDULED").count(),
    }
    return render(request, "core/dashboard.html", context)


@login_required
def privacy(request):
    return render(request, "core/privacy.html")
