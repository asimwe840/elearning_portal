from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, UpdateView, ListView
from django.urls import reverse_lazy
from .models import User, UserProfile
from .forms import UserUpdateForm, ProfileUpdateForm


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        target_user = self.get_object()
        context['enrolled_courses'] = target_user.enrollments.filter(
            status='active'
        ).select_related('course')
        context['is_own_profile'] = self.request.user == target_user
        return context


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        qs = User.objects.filter(is_active=True, is_suspended=False)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                first_name__icontains=q
            ) | qs.filter(
                last_name__icontains=q
            ) | qs.filter(
                email__icontains=q
            )
        return qs.order_by('last_name', 'first_name')


@login_required
def edit_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('users:profile', pk=request.user.pk)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(request, 'users/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


@login_required
def dashboard(request):
    from apps.courses.models import Course
    from apps.enrollment.models import Enrollment
    user = request.user

    enrolled_courses = user.enrollments.filter(
        status='active'
    ).select_related('course').order_by('-enrolled_at')[:6]

    taught_courses = []
    if user.is_teacher:
        taught_courses = user.taught_courses.filter(
            visible=True
        ).order_by('-created_at')[:6]

    # Moderator / Admin extras
    recent_users = []
    total_users = 0
    total_courses = 0
    total_enrollments = 0
    if user.is_moderator:
        recent_users = User.objects.filter(
            is_active=True
        ).order_by('-date_joined')[:8]
        total_users = User.objects.filter(is_active=True).count()
        total_courses = Course.objects.filter(visible=True).count()
        total_enrollments = Enrollment.objects.filter(status='active').count()

    context = {
        'enrolled_courses': enrolled_courses,
        'taught_courses': taught_courses,
        'recent_users': recent_users,
        'total_users': total_users,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
    }
    return render(request, 'dashboard.html', context)
