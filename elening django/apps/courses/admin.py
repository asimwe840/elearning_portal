from django.contrib import admin
from .models import (
    CourseCategory, Course, CourseSection, CourseModule,
    CoursePage, CourseFile, CourseCompletion
)


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'course_count', 'visible', 'sortorder']
    list_filter = ['visible', 'parent']
    search_fields = ['name', 'description']
    ordering = ['sortorder', 'name']


class CourseSectionInline(admin.StackedInline):
    model = CourseSection
    extra = 0
    fields = ['section', 'name', 'summary', 'visible', 'sortorder']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['shortname', 'fullname', 'category', 'teacher', 'visible',
                    'enrollment_type', 'enrolled_count', 'startdate']
    list_filter = ['visible', 'format', 'enrollment_type', 'category']
    search_fields = ['fullname', 'shortname', 'idnumber']
    ordering = ['fullname']
    inlines = [CourseSectionInline]
    fieldsets = (
        ('Basic Info', {
            'fields': ('category', 'fullname', 'shortname', 'idnumber', 'summary', 'image', 'teacher'),
        }),
        ('Format & Enrollment', {
            'fields': ('format', 'enrollment_type', 'enrolment_key', 'price', 'max_students'),
        }),
        ('Settings', {
            'fields': ('visible', 'startdate', 'enddate', 'lang', 'theme',
                       'completion_enabled', 'show_grades', 'news_items'),
        }),
    )


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'section', 'module_type', 'visible', 'sortorder']
    list_filter = ['module_type', 'visible', 'course']
    search_fields = ['name', 'course__fullname']


@admin.register(CourseCompletion)
class CourseCompletionAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'status', 'timecompleted']
    list_filter = ['status', 'course']
    search_fields = ['user__email', 'course__fullname']
