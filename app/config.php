<?php

/*=========== Database Configuraiton ==========*/

error_reporting(1);

$db_host = '127.0.0.1';
$db_user = 'root';
$db_pass = shell_exec('openssl rsautl -decrypt -inkey /home/pi/swfarereducer/keys/private_database_key.pem -in /home/pi/swfarereducer/keys/encrypt_database.dat');
$db_name = 'SWFAREREDUCERDB';

try {
	$db = new PDO("mysql:host=$db_host;dbname=$db_name;charset=UTF8",$db_user,$db_pass);
    $db->query("SET NAMES 'utf8'");
	$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
}
catch(PDOException $e) {
	error_log($e->getMessage());
	die("A database error was encountered");
}

?>
