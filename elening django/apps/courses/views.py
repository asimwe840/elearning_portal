from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.users.mixins import TeacherRequiredMixin
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count
from .models import Course, CourseCategory, CourseSection, CourseModule
from .forms import CourseForm, CourseSectionForm


class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 12

    def get_queryset(self):
        qs = Course.objects.filter(visible=True).select_related('category', 'teacher')
        q = self.request.GET.get('q')
        category_id = self.request.GET.get('category')
        if q:
            qs = qs.filter(Q(fullname__icontains=q) | Q(shortname__icontains=q) | Q(summary__icontains=q))
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs.annotate(student_count=Count('enrollments')).order_by('fullname')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CourseCategory.objects.filter(visible=True)
        context['selected_category'] = self.request.GET.get('category')
        return context


class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        context['sections'] = course.sections.filter(visible=True).prefetch_related('modules')
        if self.request.user.is_authenticated:
            context['is_enrolled'] = course.enrollments.filter(
                user=self.request.user, status='active'
            ).exists()
        else:
            context['is_enrolled'] = False
        context['enrolled_count'] = course.enrolled_count
        return context


class CourseCreateView(TeacherRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        messages.success(self.request, 'Course created successfully.')
        return super().form_valid(form)


class CourseUpdateView(TeacherRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Course.objects.all()
        return Course.objects.filter(teacher=self.request.user)


class CourseDeleteView(TeacherRequiredMixin, DeleteView):
    model = Course
    template_name = 'courses/course_confirm_delete.html'
    success_url = reverse_lazy('courses:list')

    def get_queryset(self):
        if self.request.user.is_staff:
            return Course.objects.all()
        return Course.objects.filter(teacher=self.request.user)


class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = CourseCategory
    template_name = 'courses/category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        context['courses'] = Course.objects.filter(
            category=category, visible=True
        ).select_related('teacher')
        context['subcategories'] = category.children.filter(visible=True)
        return context


@login_required
def course_content(request, pk):
    """Display course content/modules for enrolled students."""
    course = get_object_or_404(Course, pk=pk, visible=True)
    is_enrolled = course.enrollments.filter(user=request.user, status='active').exists()
    is_teacher = course.teacher == request.user or request.user.is_staff

    if not (is_enrolled or is_teacher):
        messages.warning(request, 'You must be enrolled to access this course content.')
        return redirect('courses:detail', pk=pk)

    sections = course.sections.filter(visible=True).prefetch_related('modules')
    return render(request, 'courses/course_content.html', {
        'course': course,
        'sections': sections,
        'is_teacher': is_teacher,
    })
