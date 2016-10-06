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
			document.location.assign("index.php");
		}
		function submitNewFlight()
		{
			document.swform.action = "submitnewflight.php";
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

$sql = "SELECT COUNT(*) FROM RESERVED_FLIGHTS WHERE CONFIRMATION_NUM='".$CONFIRMATION_NUM."' AND FIRST_NAME='".$FIRST_NAME."' AND LAST_NAME='".$LAST_NAME."'";
try {
	if ($res = $db->query($sql)) {
		if ($res->fetchColumn() == 0) {
			$command = "/usr/bin/python /home/pi/sw_flight_validator.py ".$CONFIRMATION_NUM." ".$FIRST_NAME." ".$LAST_NAME;
			exec($command, $output, $return);
	?>
			<div class="main">
				<form method="POST" name="swform">
		    		<h1><span>SW</span> <lable> FARE REDUCER </lable> </h1>
		    		<div class="inset">
		    		<p id="newresults">
		    		<?php
			    		if($return == 0) {
			    			$sql = "SELECT RESERVED_FLIGHTS.RESERVED_FLIGHT_ID,UPCOMING_FLIGHTS.DEPART_AIRPORT_CODE,UPCOMING_FLIGHTS.ARRIVE_AIRPORT_CODE,UPCOMING_FLIGHTS.DEPART_DATE_TIME,UPCOMING_FLIGHTS.FLIGHT_NUM
								FROM RESERVED_FLIGHTS
								LEFT JOIN UPCOMING_FLIGHTS
								ON UPCOMING_FLIGHTS.UPCOMING_FLIGHT_ID=RESERVED_FLIGHTS.UPCOMING_FLIGHT_ID
								LEFT JOIN WIRELESS_CARRIERS 
								WHERE CONFIRMATION_NUM='".$CONFIRMATION_NUM."' AND FIRST_NAME='".$FIRST_NAME."' AND LAST_NAME='".$LAST_NAME."'";

			    			echo "CONFIRMATION # ".$CONFIRMATION_NUM."<br>";
							echo $FIRST_NAME." ".$LAST_NAME."<br><br>";
							foreach ($output as $value) {
						    	$json = json_decode($value);
						    	$flightCount = $json->{'flightCount'};
						    	$departureDate1 = $json->{'departureDate1'};
								$flightNum1 = $json->{'flightNum1'};
								$departureCity1 = $json->{'departureCity1'};
								$TEMP = explode("-", $departureCity1);
								$DEPART_AIRPORT_CODE_1 = trim($TEMP[1]);
								$departureTime1 = $json->{'departureTime1'};
								$arrivalCity1 = $json->{'arrivalCity1'};
								$TEMP = explode("-", $arrivalCity1);
								$ARRIVE_AIRPORT_CODE_1 = trim($TEMP[1]);
								$arrivalTime1 = $json->{'arrivalTime1'};
								$fareType1 = $json->{'fareType1'};
								$departureDate2 = $json->{'departureDate2'};
								$flightNum2 = $json->{'flightNum2'};
								$departureCity2 = $json->{'departureCity2'};
								$TEMP = explode("-", $departureCity2);
								$DEPART_AIRPORT_CODE_2 = trim($TEMP[1]);
								$departureTime2 = $json->{'departureTime2'};
								$arrivalCity2 = $json->{'arrivalCity2'};
								$TEMP = explode("-", $arrivalCity2);
								$ARRIVE_AIRPORT_CODE_2 = trim($TEMP[1]);
								$arrivalTime2 = $json->{'arrivalTime2'};
								$fareType2 = $json->{'fareType2'};
							}
							$tempDate = strtotime($departureDate1);
							echo "Departure Date : ".date('D, M d, Y', $tempDate)."<br>";
							$tempDate = strtotime($departureTime1);
							echo "Depart: ".$departureCity1." (".date('h:i A', $tempDate).")<br>";
							$tempDate = strtotime($arrivalTime1);
							echo "Arrive: ".$arrivalCity1." (".date('h:i A', $tempDate).")<br>";
							echo "Fare Type : ".$fareType1."<br>";
							echo "Flight # ".$flightNum1."<br>";
					?>
							<input type="radio" name="FARE_LABEL_1" value="DOLLARS" required>&nbsp;DOLLARS&nbsp;
							<input type="radio" name="FARE_LABEL_1" value="POINTS" required>&nbsp;POINTS&nbsp;
							<input type="text" name="FARE_PRICE_1" style="width:35%;" required> <br>
					<?php
							if( strstr($flightCount, "2") ) {
								$tempDate = strtotime($departureDate2);
								echo "Departure Date : ".date('D, M d, Y', $tempDate)."<br>";
								$tempDate = strtotime($departureTime2);
								echo "Depart: ".$departureCity2." (".date('h:i A', $tempDate).")<br>";
								$tempDate = strtotime($arrivalTime2);
								echo "Arrive: ".$arrivalCity2." (".date('h:i A', $tempDate).")<br>";
								echo "Fare Type : ".$fareType2."<br>";
								echo "Flight # ".$flightNum2."<br>";
					?>
								<input type="radio" name="FARE_LABEL_2" value="DOLLARS" required>&nbsp;DOLLARS&nbsp;
								<input type="radio" name="FARE_LABEL_2" value="POINTS" required>&nbsp;POINTS&nbsp;
								<input type="text" name="FARE_PRICE_2" style="width:35%;" required> <br>
					<?php
							}
					?>
							<label>Mobile Alerts</label>
							<input type="tel" name="PHONE_NUM" style="width:40%;" placeholder="XXXXXXXXXX" maxlength="10" required>
							<select name="WIRELESS_CARRIER_ID" required>
								<option value=-1>***** SELECT *****</option>
					<?php
								$sql = "SELECT * FROM WIRELESS_CARRIERS ORDER BY CARRIER_NAME ASC";
								foreach ($db->query($sql) as $row) {
									echo "<option value=".$row['WIRELESS_CARRIER_ID'].">".$row['CARRIER_NAME']."</option>";
								}
					?>
							</select> <br>
							
							</p>
							</div>

							<input type="hidden" name="CONFIRMATION_NUM" value=<?php echo $CONFIRMATION_NUM;?>>
							<input type="hidden" name="FIRST_NAME" value=<?php echo $FIRST_NAME;?>>
							<input type="hidden" name="LAST_NAME" value=<?php echo $LAST_NAME;?>>
				 	 		<input type="hidden" name="DEPART_DATE_1" value="<?php echo $departureDate1;?>">
				 	 		<input type="hidden" name="FLIGHT_NUM_1" value="<?php echo $flightNum1;?>">
				 	 		<input type="hidden" name="DEPART_TIME_1" value="<?php echo $departureTime1;?>">
				 	 		<input type="hidden" name="ARRIVE_TIME_1" value="<?php echo $arrivalTime1;?>">
				 	 		<input type="hidden" name="ARRIVE_AIRPORT_CODE_1" value="<?php echo $ARRIVE_AIRPORT_CODE_1;?>">
				 	 		<input type="hidden" name="DEPART_AIRPORT_CODE_1" value="<?php echo $DEPART_AIRPORT_CODE_1;?>">
				 	 		<input type="hidden" name="FARE_TYPE_1" value="<?php echo $fareType1;?>">
				 	 		<input type="hidden" name="DEPART_DATE_2" value="<?php echo $departureDate2;?>">
				 	 		<input type="hidden" name="FLIGHT_NUM_2" value="<?php echo $flightNum2;?>">
				 	 		<input type="hidden" name="DEPART_TIME_2" value="<?php echo $departureTime2;?>">
				 	 		<input type="hidden" name="ARRIVE_TIME_2" value="<?php echo $arrivalTime2;?>">
				 	 		<input type="hidden" name="ARRIVE_AIRPORT_CODE_2" value="<?php echo $ARRIVE_AIRPORT_CODE_2;?>">
				 	 		<input type="hidden" name="DEPART_AIRPORT_CODE_2" value="<?php echo $DEPART_AIRPORT_CODE_2;?>">
				 	 		<input type="hidden" name="FARE_TYPE_2" value="<?php echo $fareType2;?>">

							<p class="p-container">
								<input type="submit" value="CONTINUE" onclick="submitNewFlight();">
							</p>
					<?php
						} elseif($return > 0) {
							echo "ERROR: Flight info does not exist or was entered incorrectly. <br>";
					?>
							</p>
							</div>
				 	 
							<p class="p-container">
								<input type="button" value="HOME" onclick="goHome();">
							</p>
					<?php
						}
					?>
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
    		<?php echo "ERROR: Flight already exists in our database! Update price! <br>"; ?>
			</p>
 	 		</div>

			<p class="p-container">
				<input type="button" value="HOME" onclick="goHome();">
			</p>
		</form>
		</div>
<?php
	}
} (PDOException  $e) {
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
			<input type="button" value="HOME" onclick="goHome();">
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
