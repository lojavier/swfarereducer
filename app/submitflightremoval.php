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
	</script>
</head>
 
<body>

<?php
require_once "config.php";

$CONFIRMATION_NUM = 	strtoupper(trim($_POST['CONFIRMATION_NUM']));
$FIRST_NAME = 			strtoupper(trim($_POST['FIRST_NAME']));
$LAST_NAME = 			strtoupper(trim($_POST['LAST_NAME']));
$RESERVED_FLIGHT_ID_1 = $_POST['RESERVED_FLIGHT_ID_1'];
$RESERVED_FLIGHT_ID_2 = $_POST['RESERVED_FLIGHT_ID_2'];

if(isset($RESERVED_FLIGHT_ID_1) && isset($RESERVED_FLIGHT_ID_2)) {
	$sql = "DELETE FROM RESERVED_FLIGHTS WHERE RESERVED_FLIGHT_ID IN (".$RESERVED_FLIGHT_ID_1.",".$RESERVED_FLIGHT_ID_2.")";
} elseif(isset($RESERVED_FLIGHT_ID_1) && !isset($RESERVED_FLIGHT_ID_2)) {
	$sql = "DELETE FROM RESERVED_FLIGHTS WHERE RESERVED_FLIGHT_ID=".$RESERVED_FLIGHT_ID_1;
}
$result = mysqli_query($conn, $sql);
$error1 = mysqli_error($conn);
if (!$error1) {
	$submissionMessage = "Successfully removed flight info!";
} else {
	$submissionMessage = $error1;
}

$sql = "SELECT RF.*,UF.*,A.AIRPORT_NAME AS DEPART_AIRPORT_NAME,B.AIRPORT_NAME AS ARRIVE_AIRPORT_NAME 
		FROM RESERVED_FLIGHTS AS RF 
		LEFT JOIN UPCOMING_FLIGHTS AS UF ON UF.UPCOMING_FLIGHT_ID=RF.UPCOMING_FLIGHT_ID 
		LEFT JOIN AIRPORTS AS A ON A.AIRPORT_CODE=UF.DEPART_AIRPORT_CODE 
		LEFT JOIN AIRPORTS AS B ON B.AIRPORT_CODE=UF.ARRIVE_AIRPORT_CODE 
		WHERE RF.CONFIRMATION_NUM='".$CONFIRMATION_NUM."' AND RF.FIRST_NAME='".$FIRST_NAME."' AND RF.LAST_NAME='".$LAST_NAME."' 
		ORDER BY UF.DEPART_DATE_TIME ASC";
$result = mysqli_query($conn, $sql);
$error2 = mysqli_error($conn);
if (mysqli_num_rows($result) > 0 && !$error2) {
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
			$farePrice1 = $row['FARE_PRICE_PAID'];
		} elseif($flightCount == 2) {
			$reservedFlightId2 = $row['RESERVED_FLIGHT_ID'];
			$departureDateTime2 = $row['DEPART_DATE_TIME'];
			$flightNum2 = $row['FLIGHT_NUM'];
			$departureCity2 = $row['DEPART_AIRPORT_NAME'];
			$arrivalCity2 = $row['ARRIVE_AIRPORT_NAME'];
			$arrivalDateTime2 = $row['ARRIVE_DATE_TIME'];
			$fareType2 = $row['FARE_TYPE'];
			$fareLabel2 = $row['FARE_LABEL'];
			$farePrice2 = $row['FARE_PRICE_PAID'];
		}
	}
?>
	<div class="main">
		<form name="swform">
    		<h1><span>SW</span> <lable> FARE REDUCER </lable> </h1>
    		<div class="inset">
    		<p id="newresults">
<?php
				echo "$submissionMessage <br><br>";

	    		if($flightCount == 2) {
	    			echo $submissionMessage."<br><br>";
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
					echo $fareLabel1." ".$farePrice1."<br><br>";
					
					$tempDate = strtotime($departureDateTime2);
					echo "Departure Date : ".date('D, M d, Y', $tempDate)."<br>";
					$tempDate = strtotime($departureDateTime2);
					echo "Depart: ".$departureCity2." (".date('h:i A', $tempDate).")<br>";
					$tempDate = strtotime($arrivalDateTime2);
					echo "Arrive: ".$arrivalCity2." (".date('h:i A', $tempDate).")<br>";
					echo "Fare Type : ".$fareType2."<br>";
					echo "Flight # ".$flightNum2."<br>";
					echo $fareLabel2." ".$farePrice2."<br>";
				} elseif($flightCount == 1) {
	    			echo "CONFIRMATION # ".$CONFIRMATION_NUM."<br>";
					echo $FIRST_NAME." ".$LAST_NAME."<br><br>";
					
					$tempDate = strtotime($departureDateTime1);
					echo "Departure Date : ".date('D, M d, Y', $tempDate)."<br>";
					$tempDate = strtotime($departureTime1);
					echo "Depart: ".$departureCity1." (".date('h:i A', $tempDate).")<br>";
					$tempDate = strtotime($arrivalTime1);
					echo "Arrive: ".$arrivalCity1." (".date('h:i A', $tempDate).")<br>";
					echo "Fare Type : ".$fareType1."<br>";
					echo "Flight # ".$flightNum1."<br>";
					echo $fareLabel1." ".$farePrice1."<br>";
				} elseif($flightCount < 1) {
					echo "ERROR <br>";
				}
?>
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
		<form method="POST" name="swform">
    		<h1><span>SW</span> <lable> FARE REDUCER </lable> </h1>
    		<div class="inset">
    		<p id="newresults">
<?php
			if($error1) {
				echo "ERROR: $error1 <br>";
			} elseif ($error2) {
    			echo "ERROR: $error2 <br>";
    		} else {
    			echo "$submissionMessage <br>";
			}
?>
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