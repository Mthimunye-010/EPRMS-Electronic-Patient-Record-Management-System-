from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from audit.utils import log_action
from .forms import PatientAdministrativeForm, PatientForm, PatientSearchForm
from .models import Patient


@role_required("RECEPTIONIST", "DOCTOR", "NURSE")
def patient_list(request):
    form = PatientSearchForm(request.GET or None)
    patients = Patient.objects.filter(is_active=True)
    query = ""
    if form.is_valid() and form.cleaned_data["q"]:
        query = form.cleaned_data["q"].strip()
        patients = patients.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(hospital_number__icontains=query)
        )
        log_action(request, action="SEARCH", description="Searched patient directory.")
    page_obj = Paginator(patients, 25).get_page(request.GET.get("page"))
    return render(request, "patients/patient_list.html", {
        "form": form,
        "patients": page_obj,
        "page_obj": page_obj,
        "query": query,
    })


@role_required("RECEPTIONIST", "DOCTOR", "NURSE")
@never_cache
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk, is_active=True)
    log_action(request, action="VIEW", target=patient, description="Viewed patient record.")
    context = {"patient": patient, "appointments": patient.appointments.select_related("doctor").all()[:20]}
    context["revealed_sa_id"] = request.session.pop("revealed_sa_id_patient", None) == patient.pk
    if request.user.role in (request.user.Role.DOCTOR, request.user.Role.NURSE):
        context["history_entries"] = patient.history_entries.select_related("recorded_by").all()[:20]
        context["allergy_entries"] = patient.history_entries.filter(
            category="ALLERGY"
        ).select_related("recorded_by")[:20]
        context["medications"] = patient.medications.select_related("prescribed_by").all()[:20]
    if request.user.role == request.user.Role.DOCTOR:
        context["consultations"] = patient.consultations.select_related("doctor").all()[:20]
    return render(request, "patients/patient_detail.html", context)


@role_required("RECEPTIONIST", "DOCTOR")
@never_cache
@require_POST
def patient_sa_id_reveal(request, pk):
    patient = get_object_or_404(Patient, pk=pk, is_active=True)
    reason = request.POST.get("reason", "")
    password = request.POST.get("password", "")
    allowed_reasons = {"identity_check", "care_task", "other"}
    if reason not in allowed_reasons or not request.user.check_password(password):
        log_action(request, action="REAUTH_FAILED", target=patient, description="SA ID reveal reauthentication failed.")
        messages.error(request, "The ID number was not revealed. Check your password and purpose, then try again.")
        return redirect("patients:patient_detail", pk=patient.pk)

    request.session["revealed_sa_id_patient"] = patient.pk
    log_action(
        request,
        action="SENSITIVE_REVEAL",
        target=patient,
        description=f"Revealed full South African ID for purpose: {reason}.",
    )
    return redirect("patients:patient_detail", pk=patient.pk)


@role_required("RECEPTIONIST")
def patient_register(request):
    duplicates = []
    if request.method == "POST":
        form = PatientForm(request.POST)
        confirmed = request.POST.get("confirm_duplicate") == "yes"
        if form.is_valid():
            duplicates = Patient.find_potential_duplicates(
                sa_id_number=form.cleaned_data["sa_id_number"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                date_of_birth=form.cleaned_data["date_of_birth"],
            )
            if duplicates and not confirmed:
                log_action(request, action="DUPLICATE_FLAG", description="Potential duplicate detected during patient registration.")
                messages.warning(request, "A potential duplicate was found. Verify identity before continuing.")
            else:
                patient = form.save(commit=False)
                patient.registered_by = request.user
                patient.save()
                log_action(request, action="CREATE", target=patient, description="Registered new patient.")
                messages.success(request, f"Patient registered ({patient.hospital_number}).")
                return redirect("patients:patient_detail", pk=patient.pk)
    else:
        form = PatientForm()
    return render(request, "patients/patient_form.html", {"form": form, "duplicates": duplicates, "title": "Register Patient"})


@role_required("RECEPTIONIST")
def patient_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk, is_active=True)
    if request.method == "POST":
        form = PatientAdministrativeForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            log_action(request, action="UPDATE", target=patient, description="Updated patient administrative contact information.")
            messages.success(request, "Patient contact information updated.")
            return redirect("patients:patient_detail", pk=patient.pk)
    else:
        form = PatientAdministrativeForm(instance=patient)
    return render(request, "patients/patient_form.html", {"form": form, "duplicates": [], "title": "Update Patient Contact Information", "patient": patient})
