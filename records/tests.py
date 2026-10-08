from datetime import date

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from patients.models import Patient
from .models import Appointment, Consultation


class RecordsAccessControlTests(TestCase):
    def setUp(self):
        self.doctor = User.objects.create_user(username="doc1", password="TestPass123!", role=User.Role.DOCTOR)
        self.receptionist = User.objects.create_user(
            username="reception1", password="TestPass123!", role=User.Role.RECEPTIONIST
        )
        self.patient = Patient.objects.create(
            sa_id_number="9001015800086",
            first_name="Thabo",
            last_name="Dlamini",
            date_of_birth=date(1990, 1, 1),
            gender="M",
            registered_by=self.receptionist,
        )

    def test_receptionist_cannot_record_consultation(self):
        self.client.login(username="reception1", password="TestPass123!")
        resp = self.client.get(reverse("records:consultation_add", args=[self.patient.pk]))
        self.assertEqual(resp.status_code, 403)

    def test_doctor_can_record_consultation(self):
        self.client.login(username="doc1", password="TestPass123!")
        resp = self.client.post(
            reverse("records:consultation_add", args=[self.patient.pk]),
            {"symptoms": "Cough", "diagnosis": "Flu", "treatment_notes": "Rest and fluids", "follow_up_date": ""},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Consultation.objects.filter(patient=self.patient).count(), 1)

    def test_receptionist_can_schedule_appointment(self):
        self.client.login(username="reception1", password="TestPass123!")
        resp = self.client.post(
            reverse("records:appointment_add", args=[self.patient.pk]),
            {
                "doctor": self.doctor.pk,
                "date": "2026-09-15",
                "time": "10:00",
                "reason": "Check-up",
                "status": "SCHEDULED",
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Appointment.objects.filter(patient=self.patient).count(), 1)
