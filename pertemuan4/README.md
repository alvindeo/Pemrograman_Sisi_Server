# Panduan Praktikum Pertemuan 4: Docker Multi Container
**Mata Kuliah:** Pemrograman Sisi Server  
**Dosen Pengampu:** Ajib Susanto (@ajibsusanto)  
**Institusi:** Universitas Dian Nuswantoro (UDINUS)  
**Folder Proyek:** `pertemuan4`

---

## DAFTAR ISI
1. [Bagian 1: Dockerfile untuk Apache + PHP Web Server](#bagian-1-dockerfile-untuk-apache--php-web-server)
2. [Bagian 2: Membuat Docker Compose (Nginx + PHP-FPM + MySQL + phpMyAdmin)](#bagian-2-membuat-docker-compose-nginx--php-fpm--mysql--phpmyadmin)
3. [Bagian 3: Deployment WordPress dengan Database MySQL & Redis](#bagian-3-deployment-wordpress-dengan-database-mysql--redis)
4. [Tabel Ringkasan Port dan URL Layanan](#tabel-ringkasan-port-dan-url-layanan)

---

## 🗂️ Rekomendasi Struktur Folder di dalam `pertemuan4`

Agar file konfigurasi antar latihan tidak saling menimpa (*conflict* `Dockerfile`), seluruh tugas dapat dirapikan di dalam folder **`pertemuan4`** sebagai berikut:

```text
pertemuan4/
│
├── [Bagian 1: Apache + PHP]
│   ├── Dockerfile
│   ├── index.php
│   └── www/
│       └── index.php
│
├── latihan4/                     <-- [Bagian 2: Nginx + PHP-FPM + MySQL + phpMyAdmin]
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── default.conf
│   └── src/
│       ├── index.php
│       └── koneksi.php
│
└── wordpress_redis/              <-- [Bagian 3: WordPress + MySQL + Redis]
    └── docker-compose.yml
```

---

## BAGIAN 1: Dockerfile untuk Apache + PHP Web Server

Pada bagian ini, kita membuat custom image PHP 8.2 berbasis Apache dengan penambahan extension database MySQL (`mysqli`, `pdo`, `pdo_mysql`) serta library pengolah gambar (`gd`).

### 1. Struktur Folder
Gunakan folder **`pertemuan4`** yang sudah Anda buat:
```text
pertemuan4/
├── Dockerfile
├── index.php
└── www/
    └── index.php
```

---

### 2. File: `Dockerfile`
Buat file `Dockerfile` langsung di dalam folder **`pertemuan4/`** dan isi dengan kode berikut:

```dockerfile
FROM php:8.2-apache
WORKDIR /var/www/html

# Install dependency sistem dan ekstensi MySQL & GD
RUN apt-get update && \
    apt-get install -y libpng-dev && \
    docker-php-ext-install pdo pdo_mysql gd

# Install dan aktifkan ekstensi mysqli
RUN docker-php-ext-install mysqli && docker-php-ext-enable mysqli

# Salin source code ke web root Apache
COPY . /var/www/html/

# Atur kepemilikan folder ke www-data
RUN chown -R www-data:www-data /var/www/html

# Aktifkan module rewrite Apache
RUN a2enmod rewrite

# Buka port 80
EXPOSE 80

# Jalankan Apache di foreground
CMD ["apache2-foreground"]
```

---

### 3. File: `index.php`
Buat file `index.php` di dalam folder **`pertemuan4/`**:

```php
<?php
echo "Docker PHP Apache is running!";
?>
```

*(Dianjurkan)* Buat subfolder `www/` di dalam `pertemuan4/` dan letakkan salinan `index.php` di dalamnya agar saat di-mount menggunakan `-v ./www:/var/www/html`, file terbaca dengan baik oleh container.

---

### 4. Eksekusi Perintah di Terminal

Buka terminal VS Code (PowerShell), pastikan terminal berada di dalam direktori **`pertemuan4`**:
```powershell
cd "f:\UDINUS\SEMESTER 7\penugasan server\pertemuan4"
```

#### a. Build Image Docker
Jalankan perintah build:
```powershell
docker build -t a71b/p4 .
```
> **Catatan:** Ganti `a71b/p4` dengan format `{username}/{nama_image}` yang Anda kehendaki. Tanda titik `.` menandakan Dockerfile berada di direktori saat ini.

#### b. Jalankan (Run) Container
- **Opsi A: Menggunakan Volume Mount (Sesuai panduan modul):**
  ```powershell
  docker run -d --name apache_php_app -v ${PWD}/www:/var/www/html -p 8081:80 a71b/p4
  ```
  *(Catatan PowerShell: `${PWD}` mewakili path folder aktif saat ini).*

- **Opsi B: Tanpa Volume Mount (Menggunakan file hasil COPY saat build):**
  ```powershell
  docker run -d --name apache_php_app -p 8081:80 a71b/p4
  ```

#### c. Uji Coba di Browser
Buka browser dan akses:
👉 **[http://localhost:8081](http://localhost:8081)**  
Tampilan yang muncul: `Docker PHP Apache is running!`

#### d. Menghentikan Container
Jika sudah selesai menguji Bagian 1 dan ingin lanjut ke Bagian 2:
```powershell
docker stop apache_php_app
docker rm apache_php_app
```

---

## BAGIAN 2: Membuat Docker Compose (Nginx + PHP-FPM + MySQL + phpMyAdmin)

Pada bagian ini, arsitektur web dipisah ke dalam beberapa container yang saling terhubung:
- **Nginx Web Server** sebagai reverse proxy (port host `8081`).
- **PHP-FPM** sebagai processor script PHP (port internal `9000`).
- **MySQL 5.7** sebagai Database Server (port host `3308`).
- **phpMyAdmin** sebagai GUI database (port host `8082`).

### 1. Struktur Folder
Buat subfolder baru bernama **`latihan4`** di dalam folder `pertemuan4/`:
```text
pertemuan4/
└── latihan4/
    ├── docker-compose.yml
    ├── Dockerfile
    ├── default.conf
    └── src/
        ├── index.php
        └── koneksi.php
```

---

### 2. File: `pertemuan4/latihan4/Dockerfile`
Buat file `Dockerfile` di dalam folder `latihan4/`:

```dockerfile
FROM php:8.2-fpm
WORKDIR /var/www/html
RUN docker-php-ext-install mysqli pdo pdo_mysql
COPY ./src /var/www/html
```

---

### 3. File: `pertemuan4/latihan4/default.conf`
Buat file `default.conf` di dalam folder `latihan4/` untuk konfigurasi Nginx:

```nginx
server {
    listen 80;
    server_name localhost;
    root /var/www/html;
    index index.php index.html;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        include fastcgi_params;
        fastcgi_pass php-fpm:9000;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }

    location ~ /\.ht {
        deny all;
    }
}
```

---

### 4. File: `pertemuan4/latihan4/docker-compose.yml`
Buat file `docker-compose.yml` di dalam folder `latihan4/`:

```yaml
services:
  web:
    image: nginx:latest
    container_name: nginx_web
    ports:
      - "8081:80"
    restart: always
    volumes:
      - ./src:/var/www/html
      - ./default.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - php-fpm

  php-fpm:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: php_fpm
    restart: always
    volumes:
      - ./src:/var/www/html

  mysql-db:
    image: mysql:5.7
    container_name: mysql_db
    command: --default-authentication-plugin=mysql_native_password
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: testdb
      MYSQL_USER: user
      MYSQL_PASSWORD: password
    ports:
      - "3308:3306"

  phpmyadmin:
    image: phpmyadmin:latest
    container_name: phpmyadmin_ui
    restart: always
    ports:
      - "8082:80"
    environment:
      PMA_ARBITRARY: 1
      PMA_HOST: mysql-db
    depends_on:
      - mysql-db
```

---

### 5. File PHP di Folder `pertemuan4/latihan4/src/`

#### a. File: `src/index.php`
```php
<?php
phpinfo();
?>
```

#### b. File: `src/koneksi.php`
```php
<?php
// Gunakan nama service database dari docker-compose.yml
$servername = "mysql-db";
$username   = "user";
$password   = "password";
$dbname     = "testdb";

$conn = mysqli_connect($servername, $username, $password, $dbname);

if (!$conn) {
    die("❌ Gagal terhubung ke MySQL: " . mysqli_connect_error());
}

echo "<h1>✅ Connected successfully to MySQL in Docker!</h1>";
?>
```

---

### 6. Eksekusi Perintah di Terminal

Masuk ke folder `latihan4`:
```powershell
cd "f:\UDINUS\SEMESTER 7\penugasan server\pertemuan4\latihan4"
```

#### a. Build dan Jalankan Container
```powershell
docker compose up -d --build
```
*(Atau `docker-compose up -d --build` jika menggunakan versi lama).*

#### b. Periksa Status Container
```powershell
docker compose ps
```

#### c. Uji Coba di Browser
1. **Periksa PHP Info:**  
   👉 **[http://localhost:8081/index.php](http://localhost:8081/index.php)**  
   Pastikan ekstensi `mysqli` dan `pdo_mysql` aktif.
2. **Periksa Koneksi Database:**  
   👉 **[http://localhost:8081/koneksi.php](http://localhost:8081/koneksi.php)**  
   Output: `✅ Connected successfully to MySQL in Docker!`
3. **Buka Panel phpMyAdmin:**  
   👉 **[http://localhost:8082](http://localhost:8082)**  
   - **Server:** `mysql-db`
   - **Username:** `root` (atau `user`)
   - **Password:** `root` (atau `password`)

#### d. Perintah Berhenti dan Rebuild
- **Menghentikan container:**
  ```powershell
  docker compose down
  ```
- **Rebuild ulang (jika ada perubahan kode/konfigurasi):**
  ```powershell
  docker compose down
  docker compose up -d --build
  ```

---

## BAGIAN 3: Deployment WordPress dengan Database MySQL & Redis

### Konsep Singkat
WordPress dipadukan dengan **Redis** sebagai *In-Memory Object Cache*. Setiap query MySQL yang sering berulang akan disimpan di memori RAM Redis, sehingga website menjadi jauh lebih cepat dan responsif.

---

### 1. Struktur Folder
Buat subfolder baru bernama **`wordpress_redis`** di dalam folder `pertemuan4/`:
```text
pertemuan4/
└── wordpress_redis/
    └── docker-compose.yml
```

---

### 2. File: `pertemuan4/wordpress_redis/docker-compose.yml`
Buat file `docker-compose.yml` di dalam folder `wordpress_redis/`:

```yaml
services:
  # 1. Database MySQL untuk WordPress
  db:
    image: mysql:8.0
    container_name: wp_mysql
    restart: always
    command: --default-authentication-plugin=mysql_native_password
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword123
      MYSQL_DATABASE: wordpress_db
      MYSQL_USER: wp_user
      MYSQL_PASSWORD: wppassword123
    volumes:
      - db_data:/var/lib/mysql
    networks:
      - wp_network

  # 2. Redis In-Memory Cache
  redis:
    image: redis:7-alpine
    container_name: wp_redis
    restart: always
    command: redis-server --save 60 1 --loglevel warning
    volumes:
      - redis_data:/data
    networks:
      - wp_network

  # 3. WordPress Web Server
  wordpress:
    image: wordpress:latest
    container_name: wp_app
    restart: always
    ports:
      - "8080:80"
    environment:
      WORDPRESS_DB_HOST: db:3306
      WORDPRESS_DB_NAME: wordpress_db
      WORDPRESS_DB_USER: wp_user
      WORDPRESS_DB_PASSWORD: wppassword123
      # Otomatisasi konfigurasi Redis ke wp-config.php
      WORDPRESS_CONFIG_EXTRA: |
        define('WP_REDIS_HOST', 'redis');
        define('WP_REDIS_PORT', 6379);
        define('WP_CACHE', true);
    volumes:
      - wordpress_data:/var/www/html
    depends_on:
      - db
      - redis
    networks:
      - wp_network

  # 4. phpMyAdmin (Opsional: memudahkan melihat tabel database WordPress)
  phpmyadmin:
    image: phpmyadmin:latest
    container_name: wp_phpmyadmin
    restart: always
    ports:
      - "8083:80"
    environment:
      PMA_HOST: db
    depends_on:
      - db
    networks:
      - wp_network

volumes:
  db_data:
  wordpress_data:
  redis_data:

networks:
  wp_network:
    driver: bridge
```

---

### 3. Langkah Eksekusi & Konfigurasi

#### Langkah 1: Masuk Direktori dan Jalankan Container
Buka terminal VS Code:
```powershell
cd "f:\UDINUS\SEMESTER 7\penugasan server\pertemuan4\wordpress_redis"
docker compose up -d
```
Cek status container:
```powershell
docker compose ps
```

#### Langkah 2: Setup WordPress via Browser
1. Buka browser: 👉 **[http://localhost:8080](http://localhost:8080)**
2. Pilih bahasa, klik **Continue**.
3. Lengkapi form instalasi WordPress:
   - **Site Title:** Blog Praktikum Docker
   - **Username:** `admin` (atau nama Anda)
   - **Password:** buat password yang mudah diingat
   - **Your Email:** email Anda
4. Klik **Install WordPress**, lalu klik **Log In** ke Dashboard.

#### Langkah 3: Install & Aktifkan Plugin Redis Object Cache
1. Di Dashboard WordPress, klik menu **Plugins** > **Add New Plugin**.
2. Cari plugin: **`Redis Object Cache`** (pembuat: *Till Krüss*).
3. Klik **Install Now**, kemudian klik **Activate**.
4. Buka menu: **Settings** > **Redis**.
5. Klik tombol **Enable Object Cache**.
6. Status koneksi akan menunjukkan:
   - **Status:** `Connected`
   - **Host:** `redis:6379`

#### Langkah 4: Verifikasi Cache Real-Time di Terminal
Jalankan perintah monitor di terminal:
```powershell
docker exec -it wp_redis redis-cli monitor
```
Lalu kembali ke browser dan refresh halaman WordPress Anda. Di terminal akan muncul aktivitas query Redis secara *live* (`GET`, `SET`, `EXISTS`). Tekan `Ctrl + C` untuk keluar dari monitor.

#### Langkah 5: Menghentikan Proyek WordPress
- **Menghentikan container (data tetap aman di volume):**
  ```powershell
  docker compose down
  ```
- **Reset total container beserta seluruh data database:**
  ```powershell
  docker compose down -v
  ```

---

## TABEL RINGKASAN PORT DAN URL LAYANAN

| Bagian | Layanan | Port Host:Container | URL Akses | Akun Default |
|---|---|---|---|---|
| **Bagian 1** | Apache + PHP Single Container | `8081:80` | `http://localhost:8081` | - |
| **Bagian 2** | Nginx Web Server (PHP-FPM) | `8081:80` | `http://localhost:8081/index.php` | - |
| **Bagian 2** | MySQL 5.7 Database | `3308:3306` | Host: `mysql-db` | user: `user` / `password` |
| **Bagian 2** | phpMyAdmin Latihan 4 | `8082:80` | `http://localhost:8082` | root / `root` |
| **Bagian 3** | WordPress CMS | `8080:80` | `http://localhost:8080` | Sesuai saat instalasi |
| **Bagian 3** | Redis Cache | Internal `6379` | Host: `redis` | Tanpa password |
| **Bagian 3** | phpMyAdmin WordPress DB | `8083:80` | `http://localhost:8083` | root / `rootpassword123` |
