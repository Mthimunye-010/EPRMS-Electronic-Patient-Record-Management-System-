from django.conf import settings
from django.db import models


class MedicalHistoryEntry(models.Model):
    class Category(models.TextChoices):
        ALLERGY = "ALLERGY", "Allergy"
        CHRONIC_CONDITION = "CHRONIC", "Chronic condition"
        SURGERY = "SURGERY", "Past surgery"
        FAMILY_HISTORY = "FAMILY", "Family history"
        OTHER = "OTHER", "Other"

    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="history_entries")
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    description = models.TextField()
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"{self.get_category_display()} - {self.patient.hospital_number}"


class Consultation(models.Model):
    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="consultations")
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="consultations_conducted", limit_choices_to={"role": "DOCTOR"})
    date = models.DateTimeField(auto_now_add=True)
    symptoms = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    treatment_notes = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"Consultation for {self.patient.hospital_number} on {self.date:%Y-%m-%d}"


class Medication(models.Model):
    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="medications")
    consultation = models.ForeignKey(Consultation, on_delete=models.SET_NULL, null=True, blank=True, related_name="medications")
    name = models.CharField(max_length=150)
    dosage = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=100, blank=True)
    prescribed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.name} - {self.patient.hospital_number}"


class Appointment(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        NO_SHOW = "NO_SHOW", "No show"

    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="appointments")
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="appointments", limit_choices_to={"role__in": ["DOCTOR", "NURSE"]})
    scheduled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="appointments_scheduled")
    date = models.DateField()
    time = models.TimeField()
    reason = models.CharField(max_length=255, blank=True, help_text="Use administrative wording only. Do not enter diagnoses or sensitive clinical details here.")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "time"]

    def __str__(self):
        return f"{self.patient.hospital_number} on {self.date} {self.time}"
