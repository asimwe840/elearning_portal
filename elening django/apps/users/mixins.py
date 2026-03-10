from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect


class TeacherRequiredMixin(LoginRequiredMixin):
    """Only teachers, moderators, and admins can access this view."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_teacher:
            messages.error(request, "You must be a teacher to access this page.")
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)


class ModeratorRequiredMixin(LoginRequiredMixin):
    """Only moderators and admins can access this view."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_moderator:
            messages.error(request, "You do not have permission to access this page.")
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(LoginRequiredMixin):
    """Only system admins (role=admin or is_staff) can access this view."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_admin_role or request.user.is_staff):
            messages.error(request, "Administrator access required.")
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)
