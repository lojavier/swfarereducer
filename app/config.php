<?php

/*=========== Database Configuration ==========*/

error_reporting(E_ALL);

$SW_SCRIPTS_PATH = "/home/pi/swfarereducer/scripts";

$db_host = "127.0.0.1";
$db_user = "root";
$db_pass = trim(shell_exec('openssl rsautl -decrypt -inkey /home/pi/swfarereducer/keys/private_database_key.pem -in /home/pi/swfarereducer/keys/encrypt_database.dat'));
$db_name = 'SWFAREREDUCERDB';

// Create connection
$conn = mysqli_connect($db_host, $db_user, $db_pass, $db_name);

// Check connection
if (!$conn) {
    die("Connection failed: " . mysqli_connect_error());
}

?>
