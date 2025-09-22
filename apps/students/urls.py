from django.urls import path
from . import views

urlpatterns = [
    path('exam/<str:exam_link>/', views.exam_access, name='student-exam-access'),
    path('compatibility-checks/', views.compatibility_checks,
         name='compatibility-checks'),
    path('launch-exam/', views.launch_exam, name='launch-exam'),
    path('seb-config/<str:exam_link>/',
         views.download_seb_config, name='download-seb-config'),
    path('complete-exam/', views.complete_exam, name='complete-exam'),
]
