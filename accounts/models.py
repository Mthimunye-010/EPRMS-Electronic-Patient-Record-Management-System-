from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model for hospital staff.

    Roles map directly to the user groups described in the project scope:
    doctors, nurses, receptionists and administrators.
    """

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        DOCTOR = "DOCTOR", "Doctor"
        NURSE = "NURSE", "Nurse"
        RECEPTIONIST = "RECEPTIONIST", "Receptionist"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.RECEPTIONIST,
        help_text="Determines what this user is allowed to do in the system.",
    )
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        help_text="Internal hospital staff/employee number.",
    )
    department = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_active_staff = models.BooleanField(
        default=True,
        help_text="Uncheck to disable this staff member's access without deleting their account.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def is_doctor(self):
        return self.role == self.Role.DOCTOR

    @property
    def is_nurse(self):
        return self.role == self.Role.NURSE

    @property
    def is_receptionist(self):
        return self.role == self.Role.RECEPTIONIST

    @property
    def is_clinical_staff(self):
        """Doctors and nurses can both add clinical notes."""
        return self.role in (self.Role.DOCTOR, self.Role.NURSE)
