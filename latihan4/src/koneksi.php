<?php
$servername = "mysql-db";
$username   = "user";
$password   = "password";
$dbname     = "testdb";

$conn = mysqli_connect($servername, $username, $password, $dbname);

if (!$conn) {
    die(" Gagal terhubung ke MySQL: " . mysqli_connect_error());
}

echo "<h1> Connected successfully to MySQL in Docker!</h1>";
?>