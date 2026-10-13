# Panduan Praktikum Pertemuan 5: Aplikasi Django Menggunakan Docker
**Mata Kuliah:** Pemrograman Sisi Server  
**Dosen Pengampu:** Ajib Susanto (@ajibsusanto)  
**Institusi:** Universitas Dian Nuswantoro (UDINUS)  

---

## DAFTAR ISI
1. [Rekomendasi Struktur Folder Proyek](#rekomendasi-struktur-folder-proyek)
2. [Trik Penting: Siklus Hidup Container Django (Mencegah Container Crash)](#trik-penting-siklus-hidup-container-django)
3. [BAGIAN 1: Deploy Aplikasi Django (Studi Kasus: Simple_LMS)](#bagian-1-deploy-aplikasi-django-studi-kasus-simple_lms)
   - [Langkah 1: Membuat File Konfigurasi Awal](#langkah-1-membuat-file-konfigurasi-awal)
   - [Langkah 2: Build & Menjalankan Container Pertama Kali](#langkah-2-build--menjalankan-container-pertama-kali)
   - [Langkah 3: Generate Project Django & App Core](#langkah-3-generate-project-django--app-core)
   - [Langkah 4: Konfigurasi Database PostgreSQL (local_settings.py)](#langkah-4-konfigurasi-database-postgresql-local_settingspy)
   - [Langkah 5: Migrasi Database ke PostgreSQL](#langkah-5-migrasi-database-ke-postgresql)
   - [Langkah 6: Mengubah Command ke Runserver & Restart Container](#langkah-6-mengubah-command-ke-runserver--restart-container)
   - [Langkah 7: Membuat Superuser & Pengujian di Browser](#langkah-7-membuat-superuser--pengujian-di-browser)
4. [BAGIAN 2: Deploy Aplikasi Django To-Do-List dengan Database PostgreSQL](#bagian-2-deploy-aplikasi-django-to-do-list-dengan-database-postgresql)
   - [Langkah 1: Persiapan Folder & Konfigurasi Docker](#langkah-1-persiapan-folder--konfigurasi-docker-bagian-2)
   - [Langkah 2: Generate Project & App Todo](#langkah-2-generate-project--app-todo)
   - [Langkah 3: Konfigurasi Settings & Koneksi PostgreSQL](#langkah-3-konfigurasi-settings--koneksi-postgresql)
   - [Langkah 4: Membuat Model Task (To-Do)](#langkah-4-membuat-model-task-to-do)
   - [Langkah 5: Membuat Views, URLs, dan Template UI To-Do List](#langkah-5-membuat-views-urls-dan-template-ui-to-do-list)
   - [Langkah 6: Migrasi Database & Menjalankan Server](#langkah-6-migrasi-database--menjalankan-server)
   - [Langkah 7: Pengujian Aplikasi To-Do List di Browser](#langkah-7-pengujian-aplikasi-to-do-list-di-browser)
5. [Tabel Ringkasan Port dan Akses Layanan](#tabel-ringkasan-port-dan-akses-layanan)

---

## Rekomendasi Struktur Folder Proyek

Untuk memisahkan antara proyek **Simple LMS** (Bagian 1) dan **To-Do-List** (Bagian 2), disarankan membuat folder `pertemuan5` dengan struktur berikut:

```text
pertemuan5/
│
├── 1_simple_lms/                      <-- Bagian 1: Simple LMS
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── code/
│       ├── requirements.txt
│       ├── manage.py                  (dibuat otomatis oleh django-admin)
│       ├── simplelms/
│       │   ├── settings.py
│       │   ├── local_settings.py
│       │   └── urls.py
│       └── core/
│
└── 2_todolist_app/                    <-- Bagian 2: To-Do-List App
    ├── Dockerfile
    ├── docker-compose.yml
    └── code/
        ├── requirements.txt
        ├── manage.py
        ├── todoproject/
        └── todo/
```

---

## Trik Penting: Siklus Hidup Container Django
> ⚠️ **PENTING UNTUK DIPAHAMI:**  
> Saat pertama kali container dijalankan, file `manage.py` **belum ada** (karena project Django belum dibuat).  
> Jika `docker-compose.yml` langsung menjalankan `python manage.py runserver`, container akan **langsung crash (Exit 2)** dengan error:  
> `python: can't open file '/code/manage.py': [Errno 2] No such file or directory`.
>
> **Solusi Sesuai Modul Dosen:**  
> 1. Pada tahap awal, gunakan perintah `command: sleep infinity` agar container tetap menyala.
> 2. Buat project Django menggunakan `docker exec`.
> 3. Setelah file `manage.py` terbentuk dan database termigrasi, ubah `command` menjadi `python manage.py runserver 0.0.0.0:8000`.

---

## BAGIAN 1: Deploy Aplikasi Django (Studi Kasus: Simple_LMS)

### Langkah 1: Membuat File Konfigurasi Awal

Buat folder `pertemuan5/1_simple_lms/` dan di dalamnya buat folder `code/`.

#### a. File: `pertemuan5/1_simple_lms/Dockerfile`
```dockerfile
FROM python:latest
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY code/requirements.txt /code/
RUN pip install -r requirements.txt
CMD ["sleep", "infinity"]
```

#### b. File: `pertemuan5/1_simple_lms/code/requirements.txt`
```text
django
psycopg2-binary
```

#### c. File: `pertemuan5/1_simple_lms/docker-compose.yml`
> Perhatikan: Pada tahap awal ini, baris `command: sleep infinity` **diaktifkan**, sedangkan baris `runserver` dikomentari dulu.

```yaml
services:
  django:
    container_name: simplelms
    build: .
    command: sleep infinity
    # command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./code:/code
    ports:
      - "8007:8000"
    depends_on:
      - postgres

  postgres:
    container_name: simpledb
    image: postgres:17
    restart: always
    environment:
      POSTGRES_DB: simple_lms
      POSTGRES_USER: simple_user
      POSTGRES_PASSWORD: simple_password
      PGDATA: /var/lib/postgresql/data/pgdata
    ports:
      - "5532:5432"
    volumes:
      - ./postgres-data:/var/lib/postgresql/data/pgdata
```

---

### Langkah 2: Build & Menjalankan Container Pertama Kali
Buka terminal VS Code di folder `pertemuan5/1_simple_lms/`:
```powershell
cd "f:\UDINUS\SEMESTER 7\penugasan server\pertemuan5\1_simple_lms"
docker compose up -d --build
```
Periksa apakah kedua container (`simplelms` dan `simpledb`) sudah berstatus `Up`:
```powershell
docker compose ps
```

---

### Langkah 3: Generate Project Django & App Core
Jalankan perintah berikut di terminal:

```powershell
# 1. Membuat project Django bernama simplelms di folder /code saat ini
docker exec simplelms django-admin startproject simplelms .

# 2. Membuat aplikasi (app) bernama core
docker exec simplelms python manage.py startapp core
```

Setelah langkah ini, di dalam folder lokal `code/` di laptop Anda akan otomatis muncul file `manage.py`, folder `simplelms/`, dan folder `core/`.

---

### Langkah 4: Konfigurasi Database PostgreSQL (local_settings.py)

#### a. Buat file: `code/simplelms/local_settings.py`
Isi dengan konfigurasi sesuai modul:
```python
from django.conf import settings

DEBUG = True
ALLOWED_HOSTS = ['*']

settings.INSTALLED_APPS += [
    'core',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'simple_lms',
        'USER': 'simple_user',
        'PASSWORD': 'simple_password',
        'HOST': 'simpledb',
        'PORT': '5432',
    }
}
```

#### b. Hubungkan `local_settings.py` ke `settings.py`
Buka file `code/simplelms/settings.py`, gulir ke baris paling bawah, lalu tambahkan baris berikut agar konfigurasi PostgreSQL dibaca oleh Django:
```python
# Tambahkan di baris paling bawah code/simplelms/settings.py:
try:
    from .local_settings import *
except ImportError:
    pass
```

---

### Langkah 5: Migrasi Database ke PostgreSQL
Jalankan perintah migrasi melalui terminal untuk membuat tabel-tabel bawaan Django ke database PostgreSQL `simple_lms`:

```powershell
docker exec simplelms python manage.py makemigrations
docker exec simplelms python manage.py migrate
```
Jika berhasil, akan muncul deretan status `Applying ... OK` untuk tabel auth, admin, sessions, dll.

---

### Langkah 6: Mengubah Command ke Runserver & Restart Container
Buka kembali file `pertemuan5/1_simple_lms/docker-compose.yml`, lalu tukar komentarnya menjadi:

```yaml
services:
  django:
    container_name: simplelms
    build: .
    # command: sleep infinity
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./code:/code
    ports:
      - "8007:8000"
    depends_on:
      - postgres
```

Lalu restart containernya:
```powershell
docker compose down
docker compose up -d
```

---

### Langkah 7: Membuat Superuser & Pengujian di Browser

#### a. Buat Akun Admin Django
Jalankan perintah berikut di terminal:
```powershell
docker exec -it simplelms python manage.py createsuperuser
```
Masukkan data saat diminta:
- **Username:** `admin` (atau nama Anda)
- **Email:** bebas / kosongkan tekan Enter
- **Password:** masukkan password (teks memang tidak terlihat di layar)
- **Bypass validation (jika password pendek):** ketik `y` lalu Enter.

#### b. Buka di Browser
1. **Halaman Utama Django:**  
   👉 Buka: **[http://localhost:8007](http://localhost:8007)**  
   *Output:* Halaman roket ucapan sukses Django *"The install worked successfully! Congratulations!"*.

2. **Halaman Admin Django:**  
   👉 Buka: **[http://localhost:8007/admin](http://localhost:8007/admin)**  
   *Output:* Login menggunakan username dan password superuser yang baru Anda buat tadi.

---

## BAGIAN 2: Deploy Aplikasi Django To-Do-List dengan Database PostgreSQL

Pada bagian ini, kita akan membuat aplikasi To-Do-List lengkap dengan model data, form input, checklist tugas, dan database PostgreSQL.

### Langkah 1: Persiapan Folder & Konfigurasi Docker (Bagian 2)

Buat folder `pertemuan5/2_todolist_app/` dan folder `code/` di dalamnya.

#### a. File: `pertemuan5/2_todolist_app/Dockerfile`
```dockerfile
FROM python:latest
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY code/requirements.txt /code/
RUN pip install -r requirements.txt
CMD ["sleep", "infinity"]
```

#### b. File: `pertemuan5/2_todolist_app/code/requirements.txt`
```text
django
psycopg2-binary
```

#### c. File: `pertemuan5/2_todolist_app/docker-compose.yml`
> Kita gunakan port host `8008` untuk Django dan port `5533` untuk PostgreSQL agar tidak bentrok dengan Simple LMS.

```yaml
services:
  django:
    container_name: todo_web
    build: .
    command: sleep infinity
    # command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./code:/code
    ports:
      - "8008:8000"
    depends_on:
      - postgres

  postgres:
    container_name: todo_db
    image: postgres:17
    restart: always
    environment:
      POSTGRES_DB: todolist_db
      POSTGRES_USER: todo_user
      POSTGRES_PASSWORD: todo_password
      PGDATA: /var/lib/postgresql/data/pgdata
    ports:
      - "5533:5432"
    volumes:
      - ./postgres-data:/var/lib/postgresql/data/pgdata
```

---

### Langkah 2: Generate Project & App Todo
Buka terminal VS Code di folder `pertemuan5/2_todolist_app/`:
```powershell
cd "f:\UDINUS\SEMESTER 7\penugasan server\pertemuan5\2_todolist_app"
docker compose up -d --build
```
Setelah kedua container menyala, jalankan perintah pembuatan project dan app:
```powershell
docker exec todo_web django-admin startproject todoproject .
docker exec todo_web python manage.py startapp todo
```

---

### Langkah 3: Konfigurasi Settings & Koneksi PostgreSQL

#### a. Buat file: `code/todoproject/local_settings.py`
```python
from django.conf import settings

DEBUG = True
ALLOWED_HOSTS = ['*']

settings.INSTALLED_APPS += [
    'todo',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'todolist_db',
        'USER': 'todo_user',
        'PASSWORD': 'todo_password',
        'HOST': 'todo_db',
        'PORT': '5432',
    }
}
```

#### b. Update `code/todoproject/settings.py`
Tambahkan di baris paling bawah file `code/todoproject/settings.py`:
```python
try:
    from .local_settings import *
except ImportError:
    pass
```

---

### Langkah 4: Membuat Model Task (To-Do)
Buka file `code/todo/models.py` dan ganti isinya dengan model Task berikut:

```python
from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=200, verbose_name="Judul Tugas")
    description = models.TextField(blank=True, verbose_name="Deskripsi")
    completed = models.BooleanField(default=False, verbose_name="Selesai")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat Pada")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
```

Daftarkan juga model Task ke Django Admin dengan mengedit file `code/todo/admin.py`:
```python
from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'completed', 'created_at')
    list_filter = ('completed',)
    search_fields = ('title',)
```

---

### Langkah 5: Membuat Views, URLs, dan Template UI To-Do List

#### a. Buat Views di `code/todo/views.py`:
```python
from django.shortcuts import render, redirect, get_object_or_404
from .models import Task

def task_list(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        if title:
            Task.objects.create(title=title, description=description)
        return redirect('task_list')

    tasks = Task.objects.all()
    return render(request, 'todo/index.html', {'tasks': tasks})

def toggle_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.completed = not task.completed
    task.save()
    return redirect('task_list')

def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect('task_list')
```

#### b. Buat File Routing: `code/todo/urls.py`
Buat file baru `urls.py` di dalam folder `code/todo/`:
```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('toggle/<int:task_id>/', views.toggle_task, name='toggle_task'),
    path('delete/<int:task_id>/', views.delete_task, name='delete_task'),
]
```

#### c. Hubungkan Routing ke Proyek: `code/todoproject/urls.py`
Buka file `code/todoproject/urls.py` dan ubah menjadi:
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('todo.urls')),
]
```

#### d. Buat Tampilan HTML: `code/todo/templates/todo/index.html`
Buat folder `templates/todo/` di dalam `code/todo/`, lalu buat file `index.html`:

```html
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>To-Do List Django Docker</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light py-5">
    <div class="container" style="max-width: 650px;">
        <div class="card shadow-sm border-0">
            <div class="card-header bg-primary text-white py-3">
                <h4 class="mb-0 text-center">📝 To-Do List (Django + PostgreSQL Docker)</h4>
            </div>
            <div class="card-body p-4">
                <!-- Form Tambah Tugas -->
                <form method="POST" class="mb-4">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label class="form-label fw-bold">Judul Tugas</label>
                        <input type="text" name="title" class="form-control" placeholder="Contoh: Belajar Docker Compose" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-bold">Deskripsi (Opsional)</label>
                        <textarea name="description" class="form-control" rows="2" placeholder="Detail catatan tugas..."></textarea>
                    </div>
                    <button type="submit" class="btn btn-success w-100">+ Tambah Tugas</button>
                </form>

                <hr>

                <!-- Daftar Tugas -->
                <h5 class="fw-bold mb-3">Daftar Tugas:</h5>
                {% if tasks %}
                    <ul class="list-group">
                        {% for task in tasks %}
                            <li class="list-group-item d-flex justify-content-between align-items-center {% if task.completed %}list-group-item-secondary{% endif %}">
                                <div>
                                    <span class="{% if task.completed %}text-decoration-line-through text-muted{% else %}fw-bold{% endif %}">
                                        {{ task.title }}
                                    </span>
                                    {% if task.description %}
                                        <div class="small text-muted">{{ task.description }}</div>
                                    {% endif %}
                                    <div class="badge bg-light text-dark border mt-1">{{ task.created_at|date:"d M Y, H:i" }}</div>
                                </div>
                                <div class="btn-group">
                                    <a href="{% url 'toggle_task' task.id %}" class="btn btn-sm {% if task.completed %}btn-warning{% else %}btn-outline-success{% endif %}">
                                        {% if task.completed %}Batal Selesai{% else %}✔ Selesai{% endif %}
                                    </a>
                                    <a href="{% url 'delete_task' task.id %}" class="btn btn-sm btn-outline-danger" onclick="return confirm('Hapus tugas ini?')">Hapus</a>
                                </div>
                            </li>
                        {% endfor %}
                    </ul>
                {% else %}
                    <div class="alert alert-info text-center mb-0">Belum ada tugas. Silakan tambahkan tugas baru di atas!</div>
                {% endif %}
            </div>
        </div>
    </div>
</body>
</html>
```

---

### Langkah 6: Migrasi Database & Menjalankan Server

1. **Jalankan Migrasi:**
   ```powershell
   docker exec todo_web python manage.py makemigrations
   docker exec todo_web python manage.py migrate
   ```

2. **Buat Superuser untuk Akses Admin (Opsional):**
   ```powershell
   docker exec -it todo_web python manage.py createsuperuser
   ```

3. **Ubah `command` di `docker-compose.yml` ke Runserver:**
   Buka file `pertemuan5/2_todolist_app/docker-compose.yml`, ubah bagian command:
   ```yaml
   services:
     django:
       container_name: todo_web
       build: .
       # command: sleep infinity
       command: python manage.py runserver 0.0.0.0:8000
   ```

4. **Restart Container To-Do List:**
   ```powershell
   docker compose down
   docker compose up -d
   ```

---

### Langkah 7: Pengujian Aplikasi To-Do List di Browser

1. **Buka Aplikasi To-Do List:**  
   👉 Kunjungi: **[http://localhost:8008](http://localhost:8008)**  
   - Anda dapat langsung menambahkan tugas baru.
   - Klik tombol **✔ Selesai** untuk menandai tugas telah selesai dicentang.
   - Klik tombol **Hapus** untuk menghapus tugas dari database PostgreSQL.
2. **Buka Panel Admin Django:**  
   👉 Kunjungi: **[http://localhost:8008/admin](http://localhost:8008/admin)**  
   - Login menggunakan superuser yang telah dibuat.
   - Semua data tasks tersimpan secara persisten di database PostgreSQL (`todo_db`).

---

## TABEL RINGKASAN PORT DAN AKSES LAYANAN

| Proyek | Service | Port Host:Container | URL Akses | Database / User |
|---|---|---|---|---|
| **Bagian 1: Simple LMS** | Django Web | `8007:8000` | `http://localhost:8007` | - |
| **Bagian 1: Simple LMS** | Django Admin | `8007:8000` | `http://localhost:8007/admin` | Login via `createsuperuser` |
| **Bagian 1: Simple LMS** | PostgreSQL 17 | `5532:5432` | Host: `simpledb` | DB: `simple_lms` / User: `simple_user` |
| **Bagian 2: To-Do-List** | Django Web UI | `8008:8000` | `http://localhost:8008` | - |
| **Bagian 2: To-Do-List** | Django Admin | `8008:8000` | `http://localhost:8008/admin` | Login via `createsuperuser` |
| **Bagian 2: To-Do-List** | PostgreSQL 17 | `5533:5432` | Host: `todo_db` | DB: `todolist_db` / User: `todo_user` |

---

## Tips Troubleshooting

1. **Container Langsung Berstatus Exited (Crash):**  
   Pastikan pada saat awal pertama kali build, gunakan `command: sleep infinity` terlebih dahulu sebelum menjalankan `python manage.py runserver`.
2. **Koneksi Database Ditolak (Connection Refused):**  
   Pastikan di file `local_settings.py`, nilai `'HOST'` mengacu pada nama service container database (`simpledb` atau `todo_db`), bukan `localhost`.
3. **Mengecek Log Error Container:**  
   ```powershell
   docker compose logs -f django
   ```
