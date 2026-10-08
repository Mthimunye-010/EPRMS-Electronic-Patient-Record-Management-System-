from datetime import date

from django.test import TestCase

from accounts.models import User
from patients.models import Patient
from .models import AuditLog


class AuditLogTests(TestCase):
    def setUp(self):
        self.receptionist = User.objects.create_user(
            username="reception1", password="TestPass123!", role=User.Role.RECEPTIONIST
        )

    def test_login_is_logged(self):
        # Post through the real login view (client.login() bypasses it and
        # therefore wouldn't exercise our audit-logging hook).
        self.client.post("/accounts/login/", {"username": "reception1", "password": "TestPass123!"})
        self.assertTrue(AuditLog.objects.filter(action="LOGIN", username_snapshot="reception1").exists())

    def test_patient_registration_is_logged(self):
        self.client.login(username="reception1", password="TestPass123!")
        self.client.post(
            "/patients/register/",
            {
                "sa_id_number": "9001015800086",
                "first_name": "Thabo",
                "last_name": "Dlamini",
                "date_of_birth": "1990-01-01",
                "gender": "M",
                "phone_number": "",
                "email": "",
                "address": "",
                "next_of_kin_name": "",
                "next_of_kin_phone": "",
            },
        )
        self.assertTrue(AuditLog.objects.filter(action="CREATE", target_model="Patient").exists())
