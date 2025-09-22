from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='teacher-register'),
    path('login/', views.login, name='teacher-login'),
    path('profile/', views.profile, name='teacher-profile'),
    path('profile/update/', views.update_profile, name='teacher-profile-update'),
]
