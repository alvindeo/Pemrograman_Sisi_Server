import os
import sys
import csv
from pathlib import Path

# Setup base directory agar modul simplelms dan core dapat di-import
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simplelms.settings')
import django
django.setup()

from django.contrib.auth.models import User
from core.models import Course, CourseMember

# 1. Import User
user_csv_path = BASE_DIR / 'csv_data' / 'user-data.csv'
if user_csv_path.exists():
    with open(user_csv_path, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for num, row in enumerate(reader):
            if not User.objects.filter(username=row['username']).exists():
                User.objects.create_user(
                    id=num + 2,
                    username=row['username'],
                    password=row['password'],
                    email=row['email']
                )

# 2. Import Course
course_csv_path = BASE_DIR / 'csv_data' / 'course-data.csv'
if course_csv_path.exists():
    with open(course_csv_path, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for num, row in enumerate(reader):
            if not Course.objects.filter(pk=num + 1).exists():
                Course.objects.create(
                    id=num + 1,
                    name=row['name'],
                    description=row['description'],
                    price=row['price'],
                    teacher=User.objects.get(pk=int(row['teacher']))
                )

# 3. Import CourseMember
member_csv_path = BASE_DIR / 'csv_data' / 'member-data.csv'
if member_csv_path.exists():
    with open(member_csv_path, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for num, row in enumerate(reader):
            if not CourseMember.objects.filter(pk=num + 1).exists():
                CourseMember.objects.create(
                    id=num + 1,
                    course_id=Course.objects.get(pk=int(row['course_id'])),
                    user_id=User.objects.get(pk=int(row['user_id'])),
                    roles=row['roles']
                )

print("Import data CSV selesai!")