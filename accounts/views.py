from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render

from audit.utils import log_action
from .decorators import role_required
from .forms import StaffCreationForm, StaffChangeForm, StyledAuthenticationForm
from .models import User


class StaffLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True
    authentication_form = StyledAuthenticationForm

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


@role_required("ADMIN")
def staff_list(request):
    staff = User.objects.all().order_by("role", "last_name")
    return render(request, "accounts/staff_list.html", {"staff": staff})


@role_required("ADMIN")
def staff_create(request):
    if request.method == "POST":
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            log_action(request, action="CREATE", target=user, description=f"Created staff account '{user.username}'.")
            messages.success(request, f"Staff account for {user.get_full_name() or user.username} created.")
            return redirect("accounts:staff_list")
    else:
        form = StaffCreationForm()
    return render(request, "accounts/staff_form.html", {"form": form, "title": "Add Staff Member"})


@role_required("ADMIN")
def staff_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = StaffChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            log_action(request, action="UPDATE", target=user, description=f"Updated staff account '{user.username}'.")
            messages.success(request, "Staff account updated.")
            return redirect("accounts:staff_list")
    else:
        form = StaffChangeForm(instance=user)
    return render(request, "accounts/staff_form.html", {"form": form, "title": "Edit Staff Member"})
