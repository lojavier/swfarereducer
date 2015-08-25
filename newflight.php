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

$command = "/usr/bin/wget -O 'change-air-reservation-results.html' --save-cookies=cookie --post-data='confirmationNumber=".$_POST['CONFIRMATION_NUM']."&firstName=".$_POST['FIRST_NAME']."&lastName=".$_POST['LAST_NAME']."&submit=submit' https://www.southwest.com/flight/change-air-reservation.html 2>&1";
echo $command . "<br>";
exec($command, $output, $return);
print_r($output);
echo "<br>";
print_r($return);
echo "<br>";

$file = popen("change-air-reservation-results.html","r");
while( !feof( $file ) )
{
	echo fread($file, 2048);
	flush();
	ob_flush();
}
pclose($file);

?>

</body>
</html>