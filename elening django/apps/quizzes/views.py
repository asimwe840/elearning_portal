from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Quiz, QuizAttempt, Question, QuestionResponse, Answer
from apps.enrollment.models import Enrollment


class QuizDetailView(LoginRequiredMixin, DetailView):
    model = Quiz
    template_name = 'quizzes/quiz_detail.html'
    context_object_name = 'quiz'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = self.get_object()
        user = self.request.user
        context['attempts'] = QuizAttempt.objects.filter(
            quiz=quiz, user=user
        ).order_by('-time_start')
        context['attempt_count'] = context['attempts'].count()
        context['can_attempt'] = (
            quiz.attempts_allowed == -1 or
            context['attempt_count'] < quiz.attempts_allowed
        )
        context['is_teacher'] = (
            quiz.course.teacher == user or user.is_staff
        )
        # Check if quiz is open
        now = timezone.now()
        context['is_open'] = (
            (quiz.time_open is None or now >= quiz.time_open) and
            (quiz.time_close is None or now <= quiz.time_close)
        )
        return context


@login_required
def start_attempt(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, visible=True)

    if not Enrollment.objects.filter(
        user=request.user, course=quiz.course, status='active'
    ).exists():
        messages.error(request, 'You must be enrolled to take this quiz.')
        return redirect('courses:detail', pk=quiz.course.pk)

    now = timezone.now()
    if quiz.time_open and now < quiz.time_open:
        messages.error(request, 'This quiz is not yet open.')
        return redirect('quizzes:detail', pk=pk)
    if quiz.time_close and now > quiz.time_close:
        messages.error(request, 'This quiz has closed.')
        return redirect('quizzes:detail', pk=pk)

    attempt_count = QuizAttempt.objects.filter(quiz=quiz, user=request.user).count()
    if quiz.attempts_allowed != -1 and attempt_count >= quiz.attempts_allowed:
        messages.error(request, 'You have used all your allowed attempts.')
        return redirect('quizzes:detail', pk=pk)

    attempt = QuizAttempt.objects.create(
        quiz=quiz,
        user=request.user,
        attempt_number=attempt_count + 1,
        state=QuizAttempt.STATE_IN_PROGRESS,
    )
    return redirect('quizzes:attempt', attempt_pk=attempt.pk)


@login_required
def take_attempt(request, attempt_pk):
    attempt = get_object_or_404(
        QuizAttempt, pk=attempt_pk, user=request.user, state=QuizAttempt.STATE_IN_PROGRESS
    )
    quiz = attempt.quiz

    # Check time limit
    if quiz.time_limit > 0:
        elapsed = (timezone.now() - attempt.time_start).total_seconds()
        if elapsed > quiz.time_limit:
            attempt.state = QuizAttempt.STATE_OVERDUE
            attempt.save()
            messages.warning(request, 'Time limit exceeded.')
            return redirect('quizzes:detail', pk=quiz.pk)

    questions = quiz.questions.prefetch_related('answers').order_by('sortorder')

    if request.method == 'POST':
        if 'finish' in request.POST:
            _save_responses(request, attempt, questions)
            _grade_attempt(attempt, questions)
            attempt.state = QuizAttempt.STATE_FINISHED
            attempt.time_finish = timezone.now()
            attempt.save()
            messages.success(request, 'Quiz submitted successfully.')
            return redirect('quizzes:result', attempt_pk=attempt.pk)
        else:
            _save_responses(request, attempt, questions)
            messages.success(request, 'Progress saved.')

    responses = {r.question_id: r for r in attempt.responses.prefetch_related('selected_answers')}
    time_remaining = None
    if quiz.time_limit > 0:
        elapsed = (timezone.now() - attempt.time_start).total_seconds()
        time_remaining = max(0, quiz.time_limit - elapsed)

    return render(request, 'quizzes/take_quiz.html', {
        'quiz': quiz,
        'attempt': attempt,
        'questions': questions,
        'responses': responses,
        'time_remaining': time_remaining,
    })


def _save_responses(request, attempt, questions):
    for question in questions:
        response, _ = QuestionResponse.objects.get_or_create(
            attempt=attempt, question=question
        )
        if question.question_type in [Question.QTYPE_ESSAY, Question.QTYPE_SHORTANSWER]:
            response.text_response = request.POST.get(f'q_{question.pk}', '')
            response.save()
        else:
            answer_ids = request.POST.getlist(f'q_{question.pk}')
            response.selected_answers.set(answer_ids)
            response.save()


def _grade_attempt(attempt, questions):
    total = 0
    for question in questions:
        try:
            response = attempt.responses.get(question=question)
        except QuestionResponse.DoesNotExist:
            continue

        if question.question_type == Question.QTYPE_ESSAY:
            continue  # Manual grading needed

        correct_fractions = sum(
            float(a.fraction) for a in response.selected_answers.all()
        )
        earned = max(0, correct_fractions) * float(question.default_mark)
        response.fraction = earned / float(question.default_mark) if question.default_mark else 0
        response.save()
        total += earned

    attempt.sumgrades = total
    attempt.save()


@login_required
def view_result(request, attempt_pk):
    attempt = get_object_or_404(
        QuizAttempt, pk=attempt_pk,
        user=request.user,
        state=QuizAttempt.STATE_FINISHED
    )
    questions = attempt.quiz.questions.prefetch_related('answers', 'responses').order_by('sortorder')
    responses = {r.question_id: r for r in attempt.responses.prefetch_related('selected_answers')}

    return render(request, 'quizzes/result.html', {
        'attempt': attempt,
        'questions': questions,
        'responses': responses,
    })
