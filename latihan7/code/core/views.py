from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import loader
from django.contrib.auth.models import User
from django.db.models import Max, Min, Avg, Count
from django.core import serializers
import json
from .models import Course, CourseContent, CourseMember, Comment


def core(request):
    # return HttpResponse("Selamat Datang - e-LMS!")
    return render(request, "core/home.html")


def statistik(request):
    return render(request, "core/statistik.html")


def statistik_from_api(request):
    return render(request, "core/statistik_from_api.html")


def users(request):
    myusers = User.objects.all().values()
    template = loader.get_template('all_users.html')
    context = {
        'myusers': myusers,
    }
    return HttpResponse(template.render(context, request))


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
    # Ambil semua data course
    courses = Course.objects.all()

    # Hitung statistik harga
    stats = courses.aggregate(
        max_price=Max('price'),
        min_price=Min('price'),
        avg_price=Avg('price')
    )

    # Ambil course dengan harga termurah & termahal
    cheapest = Course.objects.filter(price=stats['min_price'])
    expensive = Course.objects.filter(price=stats['max_price'])

    # Ambil course terpopuler & tidak populer (berdasarkan jumlah member)
    popular = (
        Course.objects
        .annotate(member_count=Count('coursemember'))
        .order_by('-member_count')[:5]
    )
    unpopular = (
        Course.objects
        .annotate(member_count=Count('coursemember'))
        .order_by('member_count')[:5]
    )

    # Hasil akhir
    result = {
        'course_count': courses.count(),
        'courses': stats,
        'cheapest': serializers.serialize('python', cheapest),
        'expensive': serializers.serialize('python', expensive),
        'popular': serializers.serialize('python', popular),
        'unpopular': serializers.serialize('python', unpopular),
    }

    return JsonResponse(result, safe=False)


def userStatistics(request):
    # 1️⃣ Semua user non-admin
    non_admin_users = User.objects.filter(is_staff=False, is_superuser=False)
    total_non_admin_users = non_admin_users.count()

    # 2️⃣ User yang membuat course
    users_with_courses = User.objects.filter(course__isnull=False).distinct()
    total_users_with_courses = users_with_courses.count()

    # 3️⃣ User tanpa course
    users_without_courses = non_admin_users.exclude(
        id__in=users_with_courses.values_list('id', flat=True)
    )
    total_users_without_courses = users_without_courses.count()

    # 4️⃣ Rata-rata jumlah course yang diikuti per user
    avg_courses_per_user = (
        CourseMember.objects.values('user_id')
        .annotate(total=Count('course_id'))
        .aggregate(avg_courses=Avg('total'))['avg_courses'] or 0
    )

    # 5️⃣ User yang mengikuti course terbanyak
    top_user = (
        CourseMember.objects.values('user_id')
        .annotate(total=Count('course_id'))
        .order_by('-total')
        .first()
    )

    top_user_data = {}
    if top_user:
        top_user_instance = User.objects.get(id=top_user['user_id'])
        top_user_data = {
            "id": top_user_instance.id,
            "username": top_user_instance.username,
            "email": top_user_instance.email,
            "total_courses": top_user['total']
        }

    # 6️⃣ Daftar user tanpa course sama sekali
    users_no_courses = non_admin_users.exclude(
        id__in=CourseMember.objects.values_list('user_id', flat=True)
    )
    users_no_courses_list = list(
        users_no_courses.values('id', 'username', 'email')
    )

    # 7️⃣ Total komentar (melalui member → user)
    total_comments_all = Comment.objects.count()
    total_comments_non_admin = Comment.objects.filter(
        member_id__user_id__in=non_admin_users
    ).count()

    # 8️⃣ User dengan komentar terbanyak (opsional tapi berguna)
    top_commenter = (
        Comment.objects
        .values('member_id__user_id')
        .annotate(total_comments=Count('id'))
        .order_by('-total_comments')
        .first()
    )

    top_commenter_data = {}
    if top_commenter:
        user_instance = User.objects.get(id=top_commenter['member_id__user_id'])
        top_commenter_data = {
            "id": user_instance.id,
            "username": user_instance.username,
            "email": user_instance.email,
            "total_comments": top_commenter['total_comments']
        }

    # 9️⃣ Hasil akhir
    result = {
        "total_non_admin_users": total_non_admin_users,
        "total_users_with_courses": total_users_with_courses,
        "total_users_without_courses": total_users_without_courses,
        "average_courses_per_user": avg_courses_per_user,
        "top_user": top_user_data,
        "users_no_courses": users_no_courses_list,
        "total_comments_all": total_comments_all,
        "total_comments_non_admin": total_comments_non_admin,
        "top_commenter": top_commenter_data,
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
