from django.urls import path
from . import views

app_name = 'enrollment'

urlpatterns = [
    path('my-courses/', views.MyCoursesView.as_view(), name='my_courses'),
    path('enroll/<int:course_pk>/', views.enroll_course, name='enroll'),
    path('unenroll/<int:course_pk>/', views.unenroll_course, name='unenroll'),
]
