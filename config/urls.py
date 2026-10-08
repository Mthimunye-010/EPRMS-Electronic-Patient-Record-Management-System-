from django.urls import include, path
from accounts.admin import otp_admin_site

urlpatterns = [
    path("admin/", otp_admin_site.urls),
    path("", include("core.urls")),
    path("accounts/", include("accounts.urls")),
    path("patients/", include("patients.urls")),
    path("records/", include("records.urls")),
    path("audit/", include("audit.urls")),
]
