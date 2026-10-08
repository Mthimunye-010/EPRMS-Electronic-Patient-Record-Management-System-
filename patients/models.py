from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse

sa_id_validator = RegexValidator(r"^\d{13}$", "South African ID numbers must be exactly 13 digits.")


class Patient(models.Model):
    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        OTHER = "O", "Other"

    hospital_number = models.CharField(max_length=20, unique=True, editable=False)
    sa_id_number = models.CharField(max_length=13, unique=True, validators=[sa_id_validator], verbose_name="South African ID number")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=Gender.choices)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    next_of_kin_name = models.CharField(max_length=150, blank=True)
    next_of_kin_phone = models.CharField(max_length=20, blank=True)
    registered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="patients_registered")
    is_active = models.BooleanField(default=True, help_text="Inactive patients are archived, not deleted.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["hospital_number"]),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.hospital_number})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def masked_sa_id(self):
        return "*" * 9 + self.sa_id_number[-4:] if self.sa_id_number else ""

    def get_absolute_url(self):
        return reverse("patients:patient_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        creating = self.pk is None
        super().save(*args, **kwargs)
        if creating and not self.hospital_number:
            self.hospital_number = f"HOSP-{self.pk:06d}"
            super().save(update_fields=["hospital_number", "updated_at"])

    @classmethod
    def find_potential_duplicates(cls, sa_id_number=None, first_name="", last_name="", date_of_birth=None, exclude_pk=None):
        query = models.Q()
        if sa_id_number:
            query |= models.Q(sa_id_number=sa_id_number)
        if first_name and last_name and date_of_birth:
            query |= models.Q(first_name__iexact=first_name, last_name__iexact=last_name, date_of_birth=date_of_birth)
        if not query:
            return cls.objects.none()
        qs = cls.objects.filter(query, is_active=True)
        if exclude_pk:
            qs = qs.exclude(pk=exclude_pk)
        return qs
