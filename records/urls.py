from django.urls import path

from . import views

app_name = "records"

urlpatterns = [
    path("patient/<int:patient_pk>/history/add/", views.history_add, name="history_add"),
    path("patient/<int:patient_pk>/consultation/add/", views.consultation_add, name="consultation_add"),
    path("patient/<int:patient_pk>/medication/add/", views.medication_add, name="medication_add"),
    path("patient/<int:patient_pk>/appointment/add/", views.appointment_add, name="appointment_add"),
    path("appointments/", views.appointment_list, name="appointment_list"),
    path("appointments/<int:pk>/status/", views.appointment_update_status, name="appointment_update_status"),
]
