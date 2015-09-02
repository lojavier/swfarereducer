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


// $command = "/usr/bin/wget -O 'view-reservation-to-change.html' --save-cookies=cookie --post-data='confirmationNumber=".$_POST['CONFIRMATION_NUM']."&firstName=".$_POST['FIRST_NAME']."&lastName=".$_POST['LAST_NAME']."&submit=submit' https://www.southwest.com/flight/change-air-reservation.html 2>&1";
// echo $command . "<br>";
// exec($command, $output, $return);
// print_r($output);
// echo "<br>";
// print_r($return);
// echo "<br>";
?>

	<div class="main">
		<form method="POST" name="swform">
    		<h1><span>SW</span> <lable> FARE REDUCER </lable> </h1>
    		<div class="inset">
    		<p id="newresults">
    		<?php
    		$command = "/usr/bin/python sw_flight_validator.py ".$_POST['CONFIRMATION_NUM']." ".$_POST['FIRST_NAME']." ".$_POST['LAST_NAME'];
			//echo $command . "<br>";
			exec($command, $output, $return);

			if($return == 0) {
				foreach ($output as $value) {
			    echo $value . "<br>";
				}
			}
			?>
			</p>
			</div>
 	 
			<p class="p-container">
				<input type="submit" value="CONTINUE" onclick="">
			</p>
		</form>
	</div>

</body>
</html>
