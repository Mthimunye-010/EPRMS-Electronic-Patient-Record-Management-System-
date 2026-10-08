from datetime import date

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from .models import Patient


class PatientModelTests(TestCase):
    def setUp(self):
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

    def test_hospital_number_auto_generated(self):
        self.assertTrue(self.patient.hospital_number.startswith("HOSP-"))

    def test_duplicate_detection_by_sa_id(self):
        duplicates = Patient.find_potential_duplicates(sa_id_number="9001015800086")
        self.assertEqual(duplicates.count(), 1)
        self.assertEqual(duplicates.first(), self.patient)

    def test_duplicate_detection_by_name_and_dob(self):
        duplicates = Patient.find_potential_duplicates(
            sa_id_number="0000000000000",  # different ID, e.g. typo
            first_name="Thabo",
            last_name="Dlamini",
            date_of_birth=date(1990, 1, 1),
        )
        self.assertEqual(duplicates.count(), 1)

    def test_no_false_positive_duplicate(self):
        duplicates = Patient.find_potential_duplicates(
            sa_id_number="8505055800083",
            first_name="Zanele",
            last_name="Nkosi",
            date_of_birth=date(1985, 5, 5),
        )
        self.assertEqual(duplicates.count(), 0)


class PatientAccessControlTests(TestCase):
    def setUp(self):
        self.receptionist = User.objects.create_user(
            username="reception1", password="TestPass123!", role=User.Role.RECEPTIONIST
        )
        self.doctor = User.objects.create_user(username="doc1", password="TestPass123!", role=User.Role.DOCTOR)
        self.patient = Patient.objects.create(
            sa_id_number="9001015800086",
            first_name="Thabo",
            last_name="Dlamini",
            date_of_birth=date(1990, 1, 1),
            gender="M",
            registered_by=self.receptionist,
        )

    def test_anonymous_redirected_to_login(self):
        resp = self.client.get(reverse("patients:patient_list"))
        self.assertEqual(resp.status_code, 302)

    def test_receptionist_can_register_patient(self):
        self.client.login(username="reception1", password="TestPass123!")
        resp = self.client.get(reverse("patients:patient_register"))
        self.assertEqual(resp.status_code, 200)

    def test_doctor_cannot_register_patient(self):
        self.client.login(username="doc1", password="TestPass123!")
        resp = self.client.get(reverse("patients:patient_register"))
        self.assertEqual(resp.status_code, 403)

    def test_doctor_can_view_patient(self):
        self.client.login(username="doc1", password="TestPass123!")
        resp = self.client.get(reverse("patients:patient_detail", args=[self.patient.pk]))
        self.assertEqual(resp.status_code, 200)

    def test_patient_search_by_hospital_number(self):
        self.client.login(username="reception1", password="TestPass123!")
        resp = self.client.get(reverse("patients:patient_list"), {"q": self.patient.hospital_number})
        self.assertContains(resp, "Dlamini")
