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