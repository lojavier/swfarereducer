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

// $CONFIRMATION_NUM = "B2RC4P";
// $FIRST_NAME = "LORENZO";
// $LAST_NAME = "JAVIER";

$sql = "SELECT * FROM RESERVED_FLIGHTS WHERE CONFIRMATION_NUM='".$CONFIRMATION_NUM."' AND FIRST_NAME='".$FIRST_NAME."' AND LAST_NAME='".$LAST_NAME."'";
$result = mysqli_query($conn, $sql);
$error = mysqli_error($conn);
if (mysqli_num_rows($result) == 0 && !$error) {
    $command = $SW_SCRIPTS_PATH."/sw_flight_validator.py ".$CONFIRMATION_NUM." ".$FIRST_NAME." ".$LAST_NAME;
	exec($command, $output, $return);
	echo "$command <br>";
	echo "return : $return";
	if($return == 0) {
		$sql = "SELECT RF.*,UF.*,A.AIRPORT_NAME AS DEPART_AIRPORT_NAME,B.AIRPORT_NAME AS ARRIVE_AIRPORT_NAME 
				FROM RESERVED_FLIGHTS AS RF 
				LEFT JOIN UPCOMING_FLIGHTS AS UF ON UF.UPCOMING_FLIGHT_ID=RF.RESERVED_FLIGHT_ID 
				LEFT JOIN AIRPORTS AS A ON A.AIRPORT_CODE=UF.DEPART_AIRPORT_CODE 
				LEFT JOIN AIRPORTS AS B ON B.AIRPORT_CODE=UF.ARRIVE_AIRPORT_CODE 
				WHERE RF.CONFIRMATION_NUM='".$CONFIRMATION_NUM."' AND RF.FIRST_NAME='".$FIRST_NAME."' AND RF.LAST_NAME='".$LAST_NAME."' 
				ORDER BY UF.DEPART_DATE_TIME ASC";
		$result = mysqli_query($conn, $sql);
		$error = mysqli_error($conn);
		if (mysqli_num_rows($result) > 0 && !$error) {
			$flightCount = 0;
		    while($row = mysqli_fetch_assoc($result)) {
		    	$flightCount++;
				if($flightCount == 1) {
					$reservedFlightId1 = $row['RESERVED_FLIGHT_ID'];
					$departureDateTime1 = $row['DEPART_DATE_TIME'];
					$flightNum1 = $row['FLIGHT_NUM'];
					$departureCity1 = $row['DEPART_AIRPORT_NAME'];
					$arrivalCity1 = $row['ARRIVE_AIRPORT_NAME'];
					$arrivalDateTime1 = $row['ARRIVE_DATE_TIME'];
					$fareType1 = $row['FARE_TYPE'];
					$fareLabel1 = $row['FARE_LABEL'];
					$farePricePaid1 = $row['FARE_PRICE_PAID'];
				} elseif($flightCount == 2) {
					$reservedFlightId2 = $row['RESERVED_FLIGHT_ID'];
					$departureDateTime2 = $row['DEPART_DATE_TIME'];
					$flightNum2 = $row['FLIGHT_NUM'];
					$departureCity2 = $row['DEPART_AIRPORT_NAME'];
					$arrivalCity2 = $row['ARRIVE_AIRPORT_NAME'];
					$arrivalDateTime2 = $row['ARRIVE_DATE_TIME'];
					$fareType2 = $row['FARE_TYPE'];
					$fareLabel2 = $row['FARE_LABEL'];
					$farePricePaid2 = $row['FARE_PRICE_PAID'];
				}
		    }
		}
?>
		<div class="main">
			<form method="POST" name="swform">
	    		<h1><span>SW</span> <lable> FARE REDUCER </lable> </h1>
	    		<div class="inset">
	    		<p id="newresults">
<?php
					if($flightCount == 2) {
		    			echo "CONFIRMATION # ".$CONFIRMATION_NUM."<br>";
						echo $FIRST_NAME." ".$LAST_NAME."<br><br>";

						$tempDate = strtotime($departureDateTime1);
						echo "Departure Date : ".date('D, M d, Y', $tempDate)."<br>";
						$tempDate = strtotime($departureDateTime1);
						echo "Depart: ".$departureCity1." (".date('h:i A', $tempDate).")<br>";
						$tempDate = strtotime($arrivalDateTime1);
						echo "Arrive: ".$arrivalCity1." (".date('h:i A', $tempDate).")<br>";
						echo "Fare Type : ".$fareType1."<br>";
						echo "Flight # ".$flightNum1."<br>";
						if ( strstr($fareLabel1, "DOLLARS") ) {
?>
							<input type="radio" name="FARE_LABEL_1" value="DOLLARS" checked="checked" required>&nbsp;DOLLARS&nbsp;
							<input type="radio" name="FARE_LABEL_1" value="POINTS" required>&nbsp;POINTS&nbsp;
							<input type="text" name="FARE_PRICE_PAID_1" style="width:35%;" value=<?php echo "$farePricePaid1"; ?> required> <br>
<?php
						} elseif ( strstr($fareLabel1, "POINTS")) {
?>
							<input type="radio" name="FARE_LABEL_1" value="DOLLARS" required>&nbsp;DOLLARS&nbsp;
							<input type="radio" name="FARE_LABEL_1" value="POINTS" checked="checked" required>&nbsp;POINTS&nbsp;
							<input type="text" name="FARE_PRICE_PAID_1" style="width:35%;" value=<?php echo "$farePricePaid1"; ?> required> <br>
<?php
						} else {
?>
							<input type="radio" name="FARE_LABEL_1" value="DOLLARS" required>&nbsp;DOLLARS&nbsp;
							<input type="radio" name="FARE_LABEL_1" value="POINTS" required>&nbsp;POINTS&nbsp;
							<input type="text" name="FARE_PRICE_PAID_1" style="width:35%;" value="" required> <br>
<?php
						}
						$tempDate = strtotime($departureDateTime2);
						echo "Departure Date : ".date('D, M d, Y', $tempDate)."<br>";
						$tempDate = strtotime($departureDateTime2);
						echo "Depart: ".$departureCity2." (".date('h:i A', $tempDate).")<br>";
						$tempDate = strtotime($arrivalDateTime2);
						echo "Arrive: ".$arrivalCity2." (".date('h:i A', $tempDate).")<br>";
						echo "Fare Type : ".$fareType2."<br>";
						echo "Flight # ".$flightNum2."<br>";
						if ( strstr($fareLabel2, "DOLLARS") ) {
?>
							<input type="radio" name="FARE_LABEL_2" value="DOLLARS" checked="checked" required>&nbsp;DOLLARS&nbsp;
							<input type="radio" name="FARE_LABEL_2" value="POINTS" required>&nbsp;POINTS&nbsp;
							<input type="text" name="FARE_PRICE_PAID_2" style="width:35%;" value=<?php echo "$farePricePaid2"; ?> required> <br>
<?php
						} elseif ( strstr($fareLabel2, "POINTS") ) {
?>
							<input type="radio" name="FARE_LABEL_2" value="DOLLARS" required>&nbsp;DOLLARS&nbsp;
							<input type="radio" name="FARE_LABEL_2" value="POINTS" checked="checked" required>&nbsp;POINTS&nbsp;
							<input type="text" name="FARE_PRICE_PAID_2" style="width:35%;" value=<?php echo "$farePricePaid2"; ?> required> <br>
<?php
						} else {
?>
							<input type="radio" name="FARE_LABEL_2" value="DOLLARS" required>&nbsp;DOLLARS&nbsp;
							<input type="radio" name="FARE_LABEL_2" value="POINTS" required>&nbsp;POINTS&nbsp;
							<input type="text" name="FARE_PRICE_PAID_2" style="width:35%;" value="" required> <br>
<?php
						}
					} elseif($flightCount == 1) {
		    			echo "CONFIRMATION # ".$CONFIRMATION_NUM."<br>";
						echo $FIRST_NAME." ".$LAST_NAME."<br><br>";
						
						$tempDate = strtotime($departureDateTime1);
						echo "Departure Date : ".date('D, M d, Y', $tempDate)."<br>";
						$tempDate = strtotime($departureDateTime1);
						echo "Depart: ".$departureCity1." (".date('h:i A', $tempDate).")<br>";
						$tempDate = strtotime($arrivalDateTime1);
						echo "Arrive: ".$arrivalCity1." (".date('h:i A', $tempDate).")<br>";
						echo "Fare Type : ".$fareType1."<br>";
						echo "Flight # ".$flightNum1."<br>";
						if ( strstr($fareLabel1, "DOLLARS") ) {
?>
							<input type="radio" name="FARE_LABEL_1" value="DOLLARS" checked="checked">&nbsp;DOLLARS&nbsp;
							<input type="radio" name="FARE_LABEL_1" value="POINTS">&nbsp;POINTS&nbsp;
							<input type="text" name="FARE_PRICE_PAID_1" style="width:35%;" value=<?php echo "$farePricePaid1"; ?> > <br>
<?php
						} elseif ( strstr($fareLabel1, "POINTS") ) {
?>
							<input type="radio" name="FARE_LABEL_1" value="DOLLARS">&nbsp;DOLLARS&nbsp;
							<input type="radio" name="FARE_LABEL_1" value="POINTS" checked="checked">&nbsp;POINTS&nbsp;
							<input type="text" name="FARE_PRICE_PAID_1" style="width:35%;" value=<?php echo "$farePricePaid1"; ?> > <br>
<?php
						} else {
?>
							<input type="radio" name="FARE_LABEL_1" value="DOLLARS">&nbsp;DOLLARS&nbsp;
							<input type="radio" name="FARE_LABEL_1" value="POINTS">&nbsp;POINTS&nbsp;
							<input type="text" name="FARE_PRICE_PAID_1" style="width:35%;" value="" > <br>
<?php
						}
					} elseif($flightCount < 1) {
						echo "ERROR: No flights exists in our database! <br>";
					}
?>
					<label>Mobile Alerts</label>
					<input type="tel" name="PHONE_NUM" style="width:40%;" placeholder="XXXXXXXXXX" maxlength="10" required>
					<select name="WIRELESS_CARRIER_ID" required>
						<option value=-1>***** SELECT *****</option>
<?php
						$sql = "SELECT * FROM WIRELESS_CARRIERS ORDER BY CARRIER_NAME ASC";
						$result = mysqli_query($conn, $sql);
						$error = mysqli_error($conn);
						if (mysqli_num_rows($result) > 0 && !$error) {
							$flightCount = 0;
						    while($row = mysqli_fetch_assoc($result)) {
								echo "<option value=".$row['WIRELESS_CARRIER_ID'].">".$row['CARRIER_NAME']."</option>";
							}
						}
?>
				</p>
				</div>

				<input type="hidden" name="CONFIRMATION_NUM" value=<?php echo $CONFIRMATION_NUM;?>>
				<input type="hidden" name="FIRST_NAME" value=<?php echo $FIRST_NAME;?>>
				<input type="hidden" name="LAST_NAME" value=<?php echo $LAST_NAME;?>>
	 	 		<input type="hidden" name="FLIGHT_NUM_1" value="<?php echo $flightNum1;?>">
	 	 		<input type="hidden" name="DEPART_DATE_TIME_1" value="<?php echo $departureDateTime1;?>">
	 	 		<input type="hidden" name="ARRIVE_DATE_TIME_1" value="<?php echo $arrivalDateTime1;?>">
	 	 		<input type="hidden" name="ARRIVE_AIRPORT_CODE_1" value="<?php echo $ARRIVE_AIRPORT_CODE_1;?>">
	 	 		<input type="hidden" name="DEPART_AIRPORT_CODE_1" value="<?php echo $DEPART_AIRPORT_CODE_1;?>">
	 	 		<input type="hidden" name="FARE_TYPE_1" value="<?php echo $fareType1;?>">
	 	 		<input type="hidden" name="FLIGHT_NUM_2" value="<?php echo $flightNum2;?>">
	 	 		<input type="hidden" name="DEPART_DATE_TIME_2" value="<?php echo $departureDateTime2;?>">
	 	 		<input type="hidden" name="ARRIVE_DATE_TIME_2" value="<?php echo $arrivalDateTime2;?>">
	 	 		<input type="hidden" name="ARRIVE_AIRPORT_CODE_2" value="<?php echo $ARRIVE_AIRPORT_CODE_2;?>">
	 	 		<input type="hidden" name="DEPART_AIRPORT_CODE_2" value="<?php echo $DEPART_AIRPORT_CODE_2;?>">
	 	 		<input type="hidden" name="FARE_TYPE_2" value="<?php echo $fareType2;?>">
			 	<p class="p-container">
					<input type="submit" value="CONTINUE" onclick="submitNewFlight();">
				</p>
				<p class="p-container">
					<input type="button" value="HOME" onclick="goHome();">
				</p>
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
			<?php echo "ERROR: Flight info does not exist or was entered incorrectly. <br>"; ?>
			</p>
			</div>
		 
			<p class="p-container">
				<input type="button" value="HOME" onclick="goHome();">
			</p>
		</form>
		</div>
<?php
	}
} elseif (mysqli_num_rows($result) > 0 && !$error) {
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
			<input type="button" value="HOME" onclick="goHome();">
		</p>
	</form>
	</div>
<?php
}
mysqli_close($conn);
?>
</body>
</html>
