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

	<script type="text/javascript">
		function goHome()
		{
			document.swform.action = "index.php";
			document.getElementById('swform').submit();
		}
	</script>
</head>
 
<body>

<?php
require_once "config.php";

$CONFIRMATION_NUM = strtoupper(trim($_POST['CONFIRMATION_NUM']));
$FIRST_NAME = strtoupper(trim($_POST['FIRST_NAME']));
$LAST_NAME = strtoupper(trim($_POST['LAST_NAME']));

$sql = "SELECT COUNT(*) FROM UPCOMING_FLIGHTS WHERE CONFIRMATION_NUM='".$CONFIRMATION_NUM."' AND FIRST_NAME='".$FIRST_NAME."' AND LAST_NAME='".$LAST_NAME."'";
if ($res = $db->query($sql)) {
	if ($res->fetchColumn() == 0) {
		$command = "/usr/bin/python sw_flight_validator.py ".$CONFIRMATION_NUM." ".$FIRST_NAME." ".$LAST_NAME;
		exec($command, $output, $return);
?>
		<div class="main">
			<form method="POST" name="swform">
	    		<h1><span>SW</span> <lable> FARE REDUCER </lable> </h1>
	    		<div class="inset">
	    		<p id="newresults">
	    		<?php
		    		if($return == 0) {
		    			echo "CONFIRMATION # ".$CONFIRMATION_NUM."<br>";
						echo $FIRST_NAME." ".$LAST_NAME."<br><br>";
						foreach ($output as $value) {
					    	$json = json_decode($value);
					    	$flightCount = $json->{'flightCount'};
					    	$departureDate1 = $json->{'departureDate1'};
							$flightNum1 = $json->{'flightNum1'};
							$departureCity1 = $json->{'departureCity1'};
							$departureTime1 = $json->{'departureTime1'};
							$arrivalCity1 = $json->{'arrivalCity1'};
							$arrivalTime1 = $json->{'arrivalTime1'};
							$fareType1 = $json->{'fareType1'};
							$departureDate2 = $json->{'departureDate2'};
							$flightNum2 = $json->{'flightNum2'};
							$departureCity2 = $json->{'departureCity2'};
							$departureTime2 = $json->{'departureTime2'};
							$arrivalCity2 = $json->{'arrivalCity2'};
							$arrivalTime2 = $json->{'arrivalTime2'};
							$fareType2 = $json->{'fareType2'};
						}
						echo "Departure Date : ".$departureDate1."<br>";
						echo "Depart: ".$departureCity1." (".$departureTime1.")<br>";
						echo "Arrive: ".$arrivalCity1." (".$arrivalTime1.")<br>";
						echo "Fare Type : ".$fareType1."<br>";
						echo "Flight # ".$flightNum1."<br>";
				?>
						<input type="radio" name="FARE_LABEL_1" value="DOLLARS" required>&nbsp;DOLLARS&nbsp;
						<input type="radio" name="FARE_LABEL_1" value="POINTS" required>&nbsp;POINTS&nbsp;
						<input type="text" name="FARE_PRICE_1" style="width:35%;" required> <br>
				<?php
						if( strstr($flightCount, "2") ) {
							echo "Departure Date : ".$departureDate2."<br>";
							echo "Depart: ".$departureCity2." (".$departureTime2.")<br>";
							echo "Arrive: ".$arrivalCity2." (".$arrivalTime2.")<br>";
							echo "Fare Type : ".$fareType2."<br>";
							echo "Flight # ".$flightNum2."<br>";
				?>
							<input type="radio" name="FARE_LABEL_2" value="DOLLARS" required>&nbsp;DOLLARS&nbsp;
							<input type="radio" name="FARE_LABEL_2" value="POINTS" required>&nbsp;POINTS&nbsp;
							<input type="text" name="FARE_PRICE_2" style="width:35%;" required> <br>
				<?php
						}
				?>
						<input type="text" name="PHONE_NUM" style="width:35%;" required>
						<select>
				<?php
							$sql = "SELECT * FROM WIRELESS_CARRIERS ORDER BY CARRIER_NAME ASC";
							foreach ($db->query($sql) as $row) {
								echo "<option value=".$row['WIRELESS_CARRIER_ID'].">".$row['CARRIER_NAME']."</option>";
							}
				?>
						</select> <br>
						
						</p>
						</div>
			 	 
						<p class="p-container">
							<input type="submit" value="CONTINUE" onclick="">
						</p>
				<?php
					} elseif($return > 0) {
						echo "ERROR: Flight info does not exist or was entered incorrectly. <br>";
				?>
						</p>
						</div>
			 	 
						<p class="p-container">
							<input type="submit" value="HOME" onclick="goHome();">
						</p>
				<?php
					}
				?>
			</form>
		</div>
<?php
	} else {
?>
		<div class="main">
		<form name="swform">
    		<h1><span>SW</span> <lable> FARE REDUCER </lable> </h1>
    		<div class="inset">
    		<p id="newresults">
    		<?php echo "ERROR: Flight already exists in our database! Update price! <br>"; ?>
			</p>
			</div>
 	 
			<p class="p-container">
				<input type="submit" value="HOME" onclick="goHome();">
			</p>
		</form>
		</div>
<?php
	}
} else {
?>
	<div class="main">
	<form name="swform">
		<h1><span>SW</span> <lable> FARE REDUCER </lable> </h1>
		<div class="inset">
		<p id="newresults">
		<?php echo "ERROR: Could not confirm if flight exists in our database! <br>"; ?>
		</p>
		</div>
	 
		<p class="p-container">
			<input type="submit" value="HOME" onclick="goHome();">
		</p>
	</form>
	</div>
<?php
}
$res = null;
$db = null;
?>
</body>
</html>
