from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import logout
from django.conf import settings
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.crypto import salted_hmac
from django.views.decorators.http import require_POST
from django_otp import user_has_device
from django_otp.plugins.otp_totp.models import TOTPDevice

from audit.models import AuditLog
from audit.utils import log_action
from .decorators import role_required
from .forms import StaffCreationForm, StaffChangeForm, StyledAuthenticationForm
from .models import User


class StaffLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True
    authentication_form = StyledAuthenticationForm

    def _attempt_identity(self):
        username = self.request.POST.get("username", "").strip().casefold()
        return salted_hmac(
            "eprms.login-attempt",
            username,
            secret=settings.SECRET_KEY,
            algorithm="sha256",
        ).hexdigest()[:48]

    def _is_rate_limited(self):
        cutoff = timezone.now() - timedelta(minutes=15)
        attempts = AuditLog.objects.filter(
            action=AuditLog.Action.LOGIN_FAILED,
            target_model="AuthAttempt",
            timestamp__gte=cutoff,
        )
        identity_attempts = attempts.filter(target_id=self._attempt_identity()).count()
        ip = self.request.META.get("REMOTE_ADDR")
        ip_attempts = attempts.filter(ip_address=ip).count() if ip else 0
        return identity_attempts >= 8 or ip_attempts >= 40

    def post(self, request, *args, **kwargs):
        if self._is_rate_limited():
            self.skip_attempt_log = True
            form = self.get_form()
            form.add_error(None, "Sign-in is temporarily unavailable. Please try again in 15 minutes.")
            return self.form_invalid(form)
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        if not getattr(self, "skip_attempt_log", False):
            identity = self._attempt_identity()
            ip = self.request.META.get("REMOTE_ADDR")
            AuditLog.objects.create(
                username_snapshot="unverified",
                action=AuditLog.Action.LOGIN_FAILED,
                target_model="AuthAttempt",
                target_id=identity,
                description="Credentials or authenticator code were rejected.",
                ip_address=ip,
            )
        return super().form_invalid(form)

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_active_staff:
            form.add_error(None, "Your hospital account has been disabled.")
            return self.form_invalid(form)
        response = super().form_valid(form)
        log_action(self.request, action="LOGIN", target=self.request.user, description="User logged in.")
        return response


def staff_logout(request):
    if request.method != "POST":
        return redirect("core:dashboard")
    if request.user.is_authenticated:
        log_action(request, action="LOGOUT", target=request.user, description="User logged out.")
    logout(request)
    return redirect("accounts:login")


@require_POST
def session_keepalive(request):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False}, status=401)
    if not request.user.is_active or not request.user.is_active_staff:
        logout(request)
        return JsonResponse({"ok": False}, status=401)
    return JsonResponse({"ok": True})


@role_required("ADMIN", "DOCTOR", "NURSE", "RECEPTIONIST")
def security_profile(request):
    activity = AuditLog.objects.filter(user=request.user).order_by("-timestamp")[:20]
    return render(request, "accounts/security_profile.html", {
        "activity": activity,
        "login_throttling_enabled": True,
        "mfa_enabled": user_has_device(request.user),
        "session_timeout_minutes": getattr(settings, "SESSION_INACTIVITY_TIMEOUT", 900) // 60,
    })


@role_required("ADMIN")
def staff_list(request):
    staff = User.objects.all().order_by("role", "last_name")
    enrolled_user_ids = set(TOTPDevice.objects.filter(confirmed=True).values_list("user_id", flat=True))
    return render(request, "accounts/staff_list.html", {"staff": staff, "enrolled_user_ids": enrolled_user_ids})


@role_required("ADMIN")
def staff_create(request):
    if request.method == "POST":
        form = StaffCreationForm(request.POST, actor=request.user)
        if form.is_valid():
            user = form.save()
            log_action(request, action="CREATE", target=user, description=f"Created staff account '{user.username}'.")
            messages.success(request, f"Staff account for {user.get_full_name() or user.username} created.")
            return redirect("accounts:staff_list")
        if "current_password" in form.errors:
            log_action(request, action="REAUTH_FAILED", description="Staff creation reauthentication failed.")
    else:
        form = StaffCreationForm(actor=request.user)
    return render(request, "accounts/staff_form.html", {"form": form, "title": "Add Staff Member"})


@role_required("ADMIN")
def staff_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        old_role = user.role
        old_active = user.is_active_staff
        form = StaffChangeForm(request.POST, instance=user, actor=request.user)
        if form.is_valid():
            form.save()
            changes = []
            if old_role != user.role:
                changes.append(f"role changed from {old_role} to {user.role}")
            if old_active != user.is_active_staff:
                changes.append(f"staff access {'enabled' if user.is_active_staff else 'disabled'}")
            detail = "; ".join(changes) or "staff details updated"
            log_action(request, action="UPDATE", target=user, description=f"{detail}.")
            messages.success(request, "Staff account updated.")
            return redirect("accounts:staff_list")
        if "current_password" in form.errors:
            log_action(request, action="REAUTH_FAILED", target=user, description="Staff edit reauthentication failed.")
    else:
        form = StaffChangeForm(instance=user, actor=request.user)
    return render(request, "accounts/staff_form.html", {"form": form, "title": "Edit Staff Member"})
