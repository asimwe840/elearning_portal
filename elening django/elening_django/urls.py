from django import views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

def home_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    from django.shortcuts import render
    return render(request, "home.html")

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home and dashboard
    path('', home_view, name='home'),
    path('dashboard/', login_required(lambda req: __import__('django.shortcuts', fromlist=['redirect']).redirect('users:dashboard')), name='dashboard'),

    # Authentication (django-allauth)
    path('accounts/', include('allauth.urls')),

    # Apps
    path('users/', include('apps.users.urls', namespace='users')),
    path('courses/', include('apps.courses.urls', namespace='courses')),
    path('enrollment/', include('apps.enrollment.urls', namespace='enrollment')),
    path('assignments/', include('apps.assignments.urls', namespace='assignments')),
    path('quizzes/', include('apps.quizzes.urls', namespace='quizzes')),
    path('forums/', include('apps.forums.urls', namespace='forums')),
    path('grades/', include('apps.grades.urls', namespace='grades')),
    path('messages/', include('apps.messaging.urls', namespace='messaging')),
    path('conferences/', include('apps.conferences.urls', namespace='conferences')),
    

    # CKEditor
    path('ckeditor/', include('ckeditor_uploader.urls')),

    # REST API
    path('api/', include([
        path('courses/', include('apps.courses.api_urls')),
        path('users/', include('apps.users.api_urls')),
    ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
