<!DOCTYPE html>
<html>
<head>
	<title>SW FARE REDUCER</title>
	<meta charset="utf-8">
	<link href="css/style.css" rel='stylesheet' type='text/css' />
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<script type="application/x-javascript"> addEventListener("load", function() { setTimeout(hideURLbar, 0); }, false); function hideURLbar(){ window.scrollTo(0,1); } </script>
	<!--webfonts-->
	<link href='http://fonts.googleapis.com/css?family=Open+Sans:400,300,600,700,800' rel='stylesheet' type='text.css'/>
	<!--//webfonts-->
</head>
 
<body>

<?php
// require_once "config.php";

// $data = array('8ABYGC', 'Lorenzo', 'Javier');

// $result = shell_exec('/usr/bin/python /opt/lampp/htdocs/swfarereducer2/sw_flight_validator.py ' . escapeshellarg(json_encode($data)) . ' > result.txt');

// // Decode the result
// $resultData = json_decode($result, true);

// // This will contain: array('status' => 'Yes!')
// var_dump($resultData);

// $command = escapeshellcmd('/usr/bin/python /opt/lampp/htdocs/swfarereducer2/sw_flight_validator.py 8ABYGC Lorenzo Javier 2>&1');
// $output = shell_exec($command);
// echo $output . "<br><br>";

// $command = escapeshellcmd('/opt/lampp/htdocs/swfarereducer2/sw_flight_validator.sh');
// $output = shell_exec($command);
// echo $output;

// $command = "/usr/bin/wget -O 'change-air-reservation-results.html' --post-data='confirmationNumber=8ABYGC&firstName=LORENZO&lastName=JAVIER&submit=submit' https://www.southwest.com/flight/change-air-reservation.html 2>&1";
$command = "/usr/bin/wget -O 'change-air-reservation.html' --save-cookies=cookie --post-data='confirmationNumber=".$_POST['CONFIRMATION_NUM']."&firstName=".$_POST['FIRST_NAME']."&lastName=".$_POST['LAST_NAME']."&submit=submit' https://www.southwest.com/flight/change-air-reservation.html 2>&1";
echo $command . "<br>";
// $output = shell_exec($command);
// echo $output;

exec($command, $output, $return);
print_r($output);
echo "<br>";
print_r($return);
echo "<br>";
// $command = "ifconfig";
// $output = shell_exec($command);
// echo $output;

// exec("/usr/bin/python /opt/lampp/htdocs/swfarereducer2/sw_flight_validator.py 8ABYGC Lorenzo Javier 2>&1", $output, $return);
// print_r($output);

// $file = popen($command,"r");
// while( !feof( $file ) )
// {
// 	echo fread($file, 2048);
// 	flush();
// 	ob_flush();
// }
// pclose($file);

?>

</body>
</html>