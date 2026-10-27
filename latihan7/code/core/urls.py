from django.urls import path
from . import views

urlpatterns = [
    path('', views.core, name='core'),
    path('core/', views.core, name='core'),
    path('users/', views.users, name='users'),
    path('statistik/', views.statistik, name='statistik'),
    path('statistik-api/', views.statistik_from_api, name='statistik_api'),
    path('course-stat/', views.courseStat, name='course_stat'),
    path('user-stats/', views.userStatistics, name='userStatistics'),
]
