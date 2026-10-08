from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.StaffLoginView.as_view(), name="login"),
    path("logout/", views.staff_logout, name="logout"),
    path("session/keepalive/", views.session_keepalive, name="session_keepalive"),
    path("security/", views.security_profile, name="security_profile"),
    path("staff/", views.staff_list, name="staff_list"),
    path("staff/new/", views.staff_create, name="staff_create"),
    path("staff/<int:pk>/edit/", views.staff_edit, name="staff_edit"),
]
