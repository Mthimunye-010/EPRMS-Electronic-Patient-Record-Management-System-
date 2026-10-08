from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("records", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="medicalhistoryentry",
            name="patient",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="history_entries", to="patients.patient"),
        ),
        migrations.AlterField(
            model_name="consultation",
            name="patient",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="consultations", to="patients.patient"),
        ),
        migrations.AlterField(
            model_name="consultation",
            name="doctor",
            field=models.ForeignKey(limit_choices_to={"role": "DOCTOR"}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="consultations_conducted", to="accounts.user"),
        ),
        migrations.AlterField(
            model_name="medication",
            name="patient",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="medications", to="patients.patient"),
        ),
        migrations.AlterField(
            model_name="appointment",
            name="patient",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="appointments", to="patients.patient"),
        ),
    ]
