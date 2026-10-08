from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from audit.utils import log_action
from patients.models import Patient
from .forms import AppointmentForm, ConsultationForm, MedicalHistoryForm, MedicationForm
from .models import Appointment, Consultation, MedicalHistoryEntry, Medication


@role_required("DOCTOR", "NURSE")
def history_add(request, patient_pk):
    patient = get_object_or_404(Patient, pk=patient_pk, is_active=True)
    if request.method == "POST":
        form = MedicalHistoryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.patient = patient
            entry.recorded_by = request.user
            entry.save()
            log_action(request, action="CREATE", target=entry, description="Added medical history entry.")
            messages.success(request, "Medical history entry added.")
            return redirect("patients:patient_detail", pk=patient.pk)
    else:
        form = MedicalHistoryForm()
    return render(request, "records/simple_form.html", {"form": form, "patient": patient, "title": "Add Medical History Entry"})


@role_required("DOCTOR")
def consultation_add(request, patient_pk):
    patient = get_object_or_404(Patient, pk=patient_pk, is_active=True)
    if request.method == "POST":
        form = ConsultationForm(request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.patient = patient
            consultation.doctor = request.user
            consultation.save()
            log_action(request, action="CREATE", target=consultation, description="Recorded consultation.")
            messages.success(request, "Consultation recorded.")
            return redirect("patients:patient_detail", pk=patient.pk)
    else:
        form = ConsultationForm()
    return render(request, "records/simple_form.html", {"form": form, "patient": patient, "title": "Record Consultation"})


@role_required("DOCTOR")
def medication_add(request, patient_pk):
    patient = get_object_or_404(Patient, pk=patient_pk, is_active=True)
    if request.method == "POST":
        form = MedicationForm(request.POST)
        if form.is_valid():
            medication = form.save(commit=False)
            medication.patient = patient
            medication.prescribed_by = request.user
            medication.save()
            log_action(request, action="CREATE", target=medication, description="Added medication record.")
            messages.success(request, "Medication added.")
            return redirect("patients:patient_detail", pk=patient.pk)
    else:
        form = MedicationForm()
    return render(request, "records/simple_form.html", {"form": form, "patient": patient, "title": "Add Medication"})


@role_required("RECEPTIONIST", "DOCTOR", "NURSE")
def appointment_add(request, patient_pk):
    patient = get_object_or_404(Patient, pk=patient_pk, is_active=True)
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            appointment.scheduled_by = request.user
            appointment.save()
            log_action(request, action="CREATE", target=appointment, description="Scheduled appointment.")
            messages.success(request, "Appointment scheduled.")
            return redirect("patients:patient_detail", pk=patient.pk)
    else:
        form = AppointmentForm()
    return render(request, "records/simple_form.html", {"form": form, "patient": patient, "title": "Schedule Appointment"})


@role_required("RECEPTIONIST", "DOCTOR", "NURSE")
def appointment_list(request):
    appointments = Appointment.objects.select_related("patient", "doctor").exclude(status="CANCELLED")
    return render(request, "records/appointment_list.html", {"appointments": appointments})


@role_required("RECEPTIONIST", "DOCTOR", "NURSE")
def appointment_update_status(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Appointment.Status.choices):
            appointment.status = new_status
            appointment.save(update_fields=["status"])
            log_action(request, action="UPDATE", target=appointment, description="Updated appointment status.")
            messages.success(request, "Appointment status updated.")
    return redirect("records:appointment_list")
