from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, ListView
from django.utils import timezone
from .models import Assignment, Submission, AssignmentGrade
from .forms import SubmissionForm, GradeSubmissionForm
from apps.enrollment.models import Enrollment


class AssignmentDetailView(LoginRequiredMixin, DetailView):
    model = Assignment
    template_name = 'assignments/assignment_detail.html'
    context_object_name = 'assignment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assignment = self.get_object()
        user = self.request.user
        try:
            context['my_submission'] = Submission.objects.filter(
                assignment=assignment, user=user, latest=True
            ).latest('modified_at')
        except Submission.DoesNotExist:
            context['my_submission'] = None
        context['is_teacher'] = (
            assignment.course.teacher == user or user.is_staff
        )
        context['submission_form'] = SubmissionForm(instance=context['my_submission'])
        return context


@login_required
def submit_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)

    if not Enrollment.objects.filter(
        user=request.user, course=assignment.course, status='active'
    ).exists():
        messages.error(request, 'You must be enrolled to submit.')
        return redirect('courses:detail', pk=assignment.course.pk)

    if assignment.cut_off_date and timezone.now() > assignment.cut_off_date:
        messages.error(request, 'The cut-off date has passed. Submissions are no longer accepted.')
        return redirect('assignments:detail', pk=pk)

    submission, _ = Submission.objects.get_or_create(
        assignment=assignment, user=request.user,
        defaults={'status': Submission.STATUS_DRAFT}
    )

    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            sub = form.save(commit=False)
            if 'submit_final' in request.POST:
                sub.status = Submission.STATUS_SUBMITTED
                sub.submitted_at = timezone.now()
            sub.save()
            messages.success(request, 'Submission saved.')
            return redirect('assignments:detail', pk=pk)
    else:
        form = SubmissionForm(instance=submission)

    return render(request, 'assignments/submit.html', {
        'assignment': assignment,
        'form': form,
        'submission': submission,
    })


@login_required
def grade_submission(request, submission_pk):
    submission = get_object_or_404(Submission, pk=submission_pk)
    assignment = submission.assignment

    if assignment.course.teacher != request.user and not request.user.is_staff:
        messages.error(request, 'Only teachers can grade submissions.')
        return redirect('assignments:detail', pk=assignment.pk)

    grade_obj, _ = AssignmentGrade.objects.get_or_create(submission=submission)

    if request.method == 'POST':
        form = GradeSubmissionForm(request.POST, instance=grade_obj)
        if form.is_valid():
            g = form.save(commit=False)
            g.grader = request.user
            g.save()
            messages.success(request, 'Grade saved.')
            return redirect('assignments:submissions', pk=assignment.pk)
    else:
        form = GradeSubmissionForm(instance=grade_obj)

    return render(request, 'assignments/grade.html', {
        'submission': submission,
        'assignment': assignment,
        'form': form,
    })


class SubmissionListView(LoginRequiredMixin, ListView):
    template_name = 'assignments/submission_list.html'
    context_object_name = 'submissions'

    def get_queryset(self):
        assignment = get_object_or_404(Assignment, pk=self.kwargs['pk'])
        if assignment.course.teacher != self.request.user and not self.request.user.is_staff:
            return Submission.objects.none()
        return Submission.objects.filter(
            assignment=assignment, latest=True
        ).select_related('user').order_by('user__last_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignment'] = get_object_or_404(Assignment, pk=self.kwargs['pk'])
        return context
