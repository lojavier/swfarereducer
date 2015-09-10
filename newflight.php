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
require_once "config.php";

$CONFIRMATION_NUM = strtoupper(trim($_POST['CONFIRMATION_NUM']));
$FIRST_NAME = strtoupper(trim($_POST['FIRST_NAME']));
$LAST_NAME = strtoupper(trim($_POST['LAST_NAME']));

$sql = "SELECT COUNT(*) FROM SWFAREREDUCERDB.UPCOMING_FLIGHTS WHERE CONFIRMATION_NUM='".$CONFIRMATION_NUM."' AND FIRST_NAME='".$FIRST_NAME."' AND LAST_NAME='".$LAST_NAME."'";
if ($res = $db->query($sql)) {
	if ($res->fetchColumn() == 0) {
?>
		<div class="main">
			<form method="POST" name="swform">
	    		<h1><span>SW</span> <lable> FARE REDUCER </lable> </h1>
	    		<div class="inset">
	    		<p id="newresults">
	    		<?php
					$flightCount = 0;
		    		$command = "/usr/bin/python sw_flight_validator.py ".$_POST['CONFIRMATION_NUM']." ".$_POST['FIRST_NAME']." ".$_POST['LAST_NAME'];
					exec($command, $output, $return);
					if($return == 0) {
						$flightCount++;
						foreach ($output as $value) {
					    	echo $value . "<br>";
					    	if ( strstr($value, "Fare Type") && $flightCount == 1) {
					    	?>
					    		<input type="radio" name="FARE_LABEL_1" value="DOLLARS">&nbsp;DOLLARS&nbsp;
								<input type="radio" name="FARE_LABEL_1" value="POINTS">&nbsp;POINTS&nbsp;
								<input type="text" name="FARE_PRICE_1" style="width:35%;"> <br>
					    	<?php
					    		$flightCount++;
					    	} else if ( strstr($value, "Fare Type") && $flightCount == 2) {
					    	?>
					    		<input type="radio" name="FARE_LABEL_2" value="DOLLARS">&nbsp;DOLLARS&nbsp;
								<input type="radio" name="FARE_LABEL_2" value="POINTS">&nbsp;POINTS&nbsp;
								<input type="text" name="FARE_PRICE_2" style="width:35%;"> <br>
					    	<?php
					    		$flightCount++;
					    	}
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
<?php
	} elseif ($res->fetchColumn() > 0) {
?>
		<div class="main">
			<form method="POST" name="swform">
	    		<h1><span>SW</span> <lable> FARE REDUCER </lable> </h1>
	    		<div class="inset">
	    		<p id="newresults">
	    		
				</p>
				</div>
	 	 
				<p class="p-container">
					<input type="submit" value="CONTINUE" onclick="">
				</p>
			</form>
		</div>
<?php
	}
}
$res = null;
$db = null;
?>
</body>
</html>
