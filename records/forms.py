from django import forms

from accounts.models import User
from .models import Appointment, Consultation, MedicalHistoryEntry, Medication


class BootstrapFormMixin:
    def _style(self):
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.CheckboxInput,)):
                field.widget.attrs.setdefault("class", "form-control")


class MedicalHistoryForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = MedicalHistoryEntry
        fields = ["category", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()


class ConsultationForm(BootstrapFormMixin, forms.ModelForm):
    follow_up_date = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    class Meta:
        model = Consultation
        fields = ["symptoms", "diagnosis", "treatment_notes", "follow_up_date"]
        widgets = {
            "symptoms": forms.Textarea(attrs={"rows": 3}),
            "diagnosis": forms.Textarea(attrs={"rows": 3}),
            "treatment_notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()


class MedicationForm(BootstrapFormMixin, forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))
    end_date = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    class Meta:
        model = Medication
        fields = ["name", "dosage", "frequency", "start_date", "end_date", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()


class AppointmentForm(BootstrapFormMixin, forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"}))

    class Meta:
        model = Appointment
        fields = ["doctor", "date", "time", "reason", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["doctor"].queryset = User.objects.filter(role__in=["DOCTOR", "NURSE"])
        self._style()
