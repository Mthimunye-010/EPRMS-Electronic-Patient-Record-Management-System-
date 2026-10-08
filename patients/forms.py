from django import forms
from .models import Patient


class PatientForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))

    class Meta:
        model = Patient
        fields = [
            "sa_id_number", "first_name", "last_name", "date_of_birth", "gender",
            "phone_number", "email", "address", "next_of_kin_name", "next_of_kin_phone",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != "date_of_birth":
                field.widget.attrs.setdefault("class", "form-control")

    def clean_sa_id_number(self):
        value = self.cleaned_data["sa_id_number"].strip()
        if not value.isdigit() or len(value) != 13:
            raise forms.ValidationError("South African ID numbers must be exactly 13 digits.")
        return value


class PatientAdministrativeForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["phone_number", "email", "address", "next_of_kin_name", "next_of_kin_phone"]
        widgets = {"address": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class PatientSearchForm(forms.Form):
    q = forms.CharField(required=False, label="Search", max_length=100, widget=forms.TextInput(attrs={
        "class": "form-control", "placeholder": "Search by name or hospital number..."
    }))
