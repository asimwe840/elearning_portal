from django.urls import path
from . import views

app_name = 'assignments'

urlpatterns = [
    path('<int:pk>/', views.AssignmentDetailView.as_view(), name='detail'),
    path('<int:pk>/submit/', views.submit_assignment, name='submit'),
    path('<int:pk>/submissions/', views.SubmissionListView.as_view(), name='submissions'),
    path('submission/<int:submission_pk>/grade/', views.grade_submission, name='grade'),
    
]
