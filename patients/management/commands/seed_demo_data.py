import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from patients.models import Patient
from records.models import Appointment, Consultation, MedicalHistoryEntry, Medication

FIRST_NAMES = ["Thabo", "Naledi", "Sipho", "Zanele", "Johan", "Aisha", "Lerato", "Pieter", "Nomvula", "Kabelo"]
LAST_NAMES = ["Dlamini", "Van der Merwe", "Nkosi", "Botha", "Mokoena", "Khumalo", "Steyn", "Sithole", "Naidoo", "Molefe"]
CONDITIONS = ["Hypertension", "Type 2 Diabetes", "Asthma", "Penicillin allergy", "Previous appendectomy"]
DRUGS = ["Amoxicillin", "Metformin", "Atorvastatin", "Salbutamol inhaler", "Paracetamol"]


class Command(BaseCommand):
    help = "Seed the database with synthetic staff, patients, and records for demo/testing purposes."

    def add_arguments(self, parser):
        parser.add_argument("--patients", type=int, default=15, help="Number of synthetic patients to create.")

    def handle(self, *args, **options):
        random.seed(42)

        self.stdout.write("Creating demo staff accounts...")
        admin, _ = User.objects.get_or_create(
            username="admin_demo",
            defaults=dict(first_name="Admin", last_name="User", role=User.Role.ADMIN, is_staff=True, is_superuser=True),
        )
        admin.set_password("DemoPass123!")
        admin.save()

        doctor, _ = User.objects.get_or_create(
            username="dr_ndlovu",
            defaults=dict(first_name="Sarah", last_name="Ndlovu", role=User.Role.DOCTOR, employee_id="DOC-001"),
        )
        doctor.set_password("DemoPass123!")
        doctor.save()

        nurse, _ = User.objects.get_or_create(
            username="nurse_maseko",
            defaults=dict(first_name="Palesa", last_name="Maseko", role=User.Role.NURSE, employee_id="NUR-001"),
        )
        nurse.set_password("DemoPass123!")
        nurse.save()

        receptionist, _ = User.objects.get_or_create(
            username="reception_v",
            defaults=dict(first_name="Vusi", last_name="Radebe", role=User.Role.RECEPTIONIST, employee_id="REC-001"),
        )
        receptionist.set_password("DemoPass123!")
        receptionist.save()

        self.stdout.write(f"Creating {options['patients']} synthetic patients...")
        created = 0
        for i in range(options["patients"]):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            dob = date(1950, 1, 1) + timedelta(days=random.randint(0, 25000))
            sa_id = f"{dob:%y%m%d}{random.randint(1000, 9999)}{random.randint(0,1)}{random.randint(0,1)}{random.randint(0,9)}"
            if Patient.objects.filter(sa_id_number=sa_id).exists():
                continue

            patient = Patient.objects.create(
                sa_id_number=sa_id,
                first_name=first,
                last_name=last,
                date_of_birth=dob,
                gender=random.choice(["M", "F"]),
                phone_number=f"08{random.randint(10000000, 99999999)}",
                address="Johannesburg, Gauteng",
                registered_by=receptionist,
            )
            created += 1

            MedicalHistoryEntry.objects.create(
                patient=patient,
                category=random.choice(list(MedicalHistoryEntry.Category.values)),
                description=random.choice(CONDITIONS),
                recorded_by=doctor,
            )

            consultation = Consultation.objects.create(
                patient=patient,
                doctor=doctor,
                symptoms="Routine check-up",
                diagnosis=random.choice(CONDITIONS),
                treatment_notes="Prescribed medication and follow-up scheduled.",
            )

            Medication.objects.create(
                patient=patient,
                consultation=consultation,
                name=random.choice(DRUGS),
                dosage="1 tablet",
                frequency="Twice daily",
                prescribed_by=doctor,
                start_date=timezone.localdate(),
            )

            Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                scheduled_by=receptionist,
                date=timezone.localdate() + timedelta(days=random.randint(1, 30)),
                time="09:00",
                reason="Follow-up",
            )

        self.stdout.write(self.style.SUCCESS(
            f"Done. Created {created} new patients. Demo logins (password: DemoPass123!): "
            f"admin_demo, dr_ndlovu, nurse_maseko, reception_v"
        ))
