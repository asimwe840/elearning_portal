from django.contrib import admin
from .models import Assignment, Submission, AssignmentGrade


class SubmissionInline(admin.TabularInline):
    model = Submission
    extra = 0
    readonly_fields = ['user', 'status', 'submitted_at', 'modified_at']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'submission_type', 'max_grade', 'due_date', 'visible']
    list_filter = ['submission_type', 'grading_method', 'visible', 'course']
    search_fields = ['name', 'course__fullname']
    inlines = [SubmissionInline]


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'assignment', 'status', 'submitted_at']
    list_filter = ['status', 'assignment__course']
    search_fields = ['user__email', 'assignment__name']


@admin.register(AssignmentGrade)
class AssignmentGradeAdmin(admin.ModelAdmin):
    list_display = ['submission', 'grader', 'grade', 'graded_at', 'released']
    list_filter = ['released']
