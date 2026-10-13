# Gunakan base image resmi PHP dengan Apache
FROM php:8.2-apache
# Tambahkan ServerName supaya tidak muncul warning AH00558
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf
# Aktifkan mod_rewrite (opsional, sering dipakai di web project PHP)
RUN a2enmod rewrite
# Set folder kerja
WORKDIR /var/www/html
# Copy semua file project ke dalam container
COPY . /var/www/html
# Expose port 80
EXPOSE 80
# Jalankan Apache di foreground
CMD ["apache2-foreground"]