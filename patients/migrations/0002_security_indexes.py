from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("patients", "0001_initial")]

    operations = [
        migrations.RemoveIndex(model_name="patient", name="patients_pa_sa_id_n_bd7dfd_idx"),
    ]
