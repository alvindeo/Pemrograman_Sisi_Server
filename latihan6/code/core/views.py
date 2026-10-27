from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Max, Min, Avg, Count
from .models import Course, CourseContent, CourseMember, Comment


def core(request):
    return HttpResponse("Hello World!")


def insert_user(request):
    user = User.objects.create_user(
        username="usertesting",
        email="usertest@email.com",
        password="password123"
    )
    return JsonResponse({
        "message": "User berhasil ditambahkan",
        "id": user.id,
        "username": user.username,
        "email": user.email,
    })


def insert_course(request):
    return HttpResponse("Halaman insert course")


def user_list(request):
    return HttpResponse("Halaman user list")


def user_json(request):
    return JsonResponse({"message": "Halaman user json"})


def user_detail(request, pk):
    return HttpResponse(f"Detail user {pk}")


def search_user(request):
    return HttpResponse("Search user")


def update_user(request, pk):
    return HttpResponse(f"Update user {pk}")


def delete_user(request, pk):
    return HttpResponse(f"Delete user {pk}")


def delete_all_courses(request):
    return HttpResponse("Delete all courses")


def delete_users_except(request, pk):
    return HttpResponse(f"Delete users except {pk}")


# Query Relational
def allCourse(request):
    all_course = Course.objects.all()
    result = []
    for course in all_course:
        record = {
            'id': course.id,
            'name': course.name,
            'description': course.description,
            'price': course.price,
            'teacher': {
                'id': course.teacher.id,
                'username': course.teacher.username,
                'email': course.teacher.email,
                'fullname': f"{course.teacher.first_name} {course.teacher.last_name}".strip()
            }
        }
        result.append(record)
    return JsonResponse(result, safe=False)


def userCourses(request):
    user = User.objects.get(pk=3)
    courses = Course.objects.filter(teacher=user.id)
    course_data = []
    for course in courses:
        record = {
            'id': course.id,
            'name': course.name,
            'description': course.description,
            'price': course.price
        }
        course_data.append(record)
    result = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'fullname': f"{user.first_name} {user.last_name}".strip(),
        'courses': course_data
    }
    return JsonResponse(result, safe=False)


def courseStat(request):
    courses = Course.objects.all()
    stats = courses.aggregate(
        max_price=Max('price'),
        min_price=Min('price'),
        avg_price=Avg('price')
    )
    result = {
        'course_count': len(courses),
        'courses': stats
    }
    return JsonResponse(result, safe=False)


def courseMemberStat(request):
    courses = Course.objects.filter(description__contains='python') \
        .annotate(member_num=Count('coursemember'))
    course_data = []
    for course in courses:
        record = {
            'id': course.id,
            'name': course.name,
            'price': course.price,
            'member_count': course.member_num
        }
        course_data.append(record)
    result = {
        'data_count': len(course_data),
        'data': course_data
    }
    return JsonResponse(result)
