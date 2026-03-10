from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.utils import timezone
from apps.courses.models import Course
from .models import Enrollment


@login_required
def enroll_course(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, visible=True)

    if Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.info(request, 'You are already enrolled in this course.')
        return redirect('courses:content', pk=course_pk)

    if course.is_full:
        messages.error(request, 'This course is full.')
        return redirect('courses:detail', pk=course_pk)

    if course.enrollment_type == Course.ENROL_MANUAL:
        messages.info(request, 'This course requires manual enrollment. Please contact the teacher.')
        return redirect('courses:detail', pk=course_pk)

    if course.enrollment_type == Course.ENROL_INVITE:
        messages.error(request, 'This course requires an invitation.')
        return redirect('courses:detail', pk=course_pk)

    # Check enrollment key
    if course.enrollment_type == Course.ENROL_OPEN and course.enrolment_key:
        if request.method == 'POST':
            key = request.POST.get('enrolment_key', '')
            if key != course.enrolment_key:
                messages.error(request, 'Incorrect enrollment key.')
                return render(request, 'enrollment/enroll_key.html', {'course': course})
        else:
            return render(request, 'enrollment/enroll_key.html', {'course': course})

    Enrollment.objects.create(user=request.user, course=course, enrolled_by=request.user)
    messages.success(request, f'You have successfully enrolled in "{course.fullname}".')
    return redirect('courses:content', pk=course_pk)


@login_required
def unenroll_course(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)

    if request.method == 'POST':
        enrollment.delete()
        messages.success(request, f'You have unenrolled from "{course.fullname}".')
        return redirect('courses:list')

    return render(request, 'enrollment/unenroll_confirm.html', {'course': course})


class MyCoursesView(LoginRequiredMixin, ListView):
    template_name = 'enrollment/my_courses.html'
    context_object_name = 'enrollments'

    def get_queryset(self):
        return Enrollment.objects.filter(
            user=self.request.user, status=Enrollment.STATUS_ACTIVE
        ).select_related('course', 'course__category').order_by('-enrolled_at')
