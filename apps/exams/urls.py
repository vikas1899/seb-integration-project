from django.urls import path
from . import views

urlpatterns = [
    path('', views.exam_list_create, name='exam-list-create'),
    path('<uuid:exam_id>/', views.exam_detail, name='exam-detail'),
    path('<uuid:exam_id>/duplicate/', views.duplicate_exam, name='exam-duplicate'),
    path('<uuid:exam_id>/attempts/', views.exam_attempts, name='exam-attempts'),
]
