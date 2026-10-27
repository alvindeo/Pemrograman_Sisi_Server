from django.urls import path
from . import views

urlpatterns = [
    path("core/", views.core, name="core"),
    path("insert-user/", views.insert_user, name="insert_user"),
    path("insert-course/", views.insert_course, name="insert_course"),
    path("users/", views.user_list, name="user_list"),
    path("users/json/", views.user_json, name="user_json"),
    path("users/<int:pk>/", views.user_detail, name="user_detail"),
    path("search-user/", views.search_user, name="search_user"),
    path("update-user/<int:pk>/", views.update_user, name="update_user"),
    path("delete-user/<int:pk>/", views.delete_user, name="delete_user"),
    path("delete-courses/", views.delete_all_courses, name="delete_all_courses"),
    path("delete-users-except/<int:pk>/", views.delete_users_except, name="delete_users_except"),
    path("all-courses/", views.allCourse, name="all_courses"),
    path("user-courses/", views.userCourses, name="user_courses"),
    path("courses-stat/", views.courseStat, name="courses_stat"),
    path("courses-member-stat/", views.courseMemberStat, name="courses_member_stat"),
]