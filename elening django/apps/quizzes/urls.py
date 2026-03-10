from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    path('<int:pk>/', views.QuizDetailView.as_view(), name='detail'),
    path('<int:pk>/start/', views.start_attempt, name='start'),
    path('attempt/<int:attempt_pk>/', views.take_attempt, name='attempt'),
    path('attempt/<int:attempt_pk>/result/', views.view_result, name='result'),
]
