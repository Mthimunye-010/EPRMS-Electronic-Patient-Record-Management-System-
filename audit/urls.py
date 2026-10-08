from django.urls import path

from . import views

app_name = "audit"

urlpatterns = [
    path("security/", views.security_dashboard, name="security_dashboard"),
    path("", views.audit_log_list, name="audit_log_list"),
]
