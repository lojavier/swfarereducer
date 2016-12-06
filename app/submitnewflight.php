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
$FARE_LABEL_1 = 		$_POST['FARE_LABEL_1'];
$FARE_PRICE_PAID_1 = 	$_POST['FARE_PRICE_PAID_1'];
$RESERVED_FLIGHT_ID_2 = $_POST['RESERVED_FLIGHT_ID_2'];
$FARE_LABEL_2 = 		$_POST['FARE_LABEL_2'];
$FARE_PRICE_PAID_2 = 	$_POST['FARE_PRICE_PAID_2'];
$PHONE_NUM =			$_POST['PHONE_NUM'];
$WIRELESS_CARRIER_ID =	$_POST['WIRELESS_CARRIER_ID'];

$sql = "SELECT CARRIER_TEXT_EMAIL FROM WIRELESS_CARRIERS WHERE WIRELESS_CARRIER_ID=".$WIRELESS_CARRIER_ID;
$result = mysqli_query($conn, $sql);
$error1 = mysqli_error($conn);
if (mysqli_num_rows($result) > 0 && !$error1) {
    while($row = mysqli_fetch_assoc($result)) {
    	$EMAIL = $PHONE_NUM.$row['CARRIER_TEXT_EMAIL'];
    }
} else {
	$submissionMessage = $error1;
}

$sql = "UPDATE RESERVED_FLIGHTS 
		SET FARE_LABEL=
		(CASE
		    WHEN RESERVED_FLIGHT_ID=".$RESERVED_FLIGHT_ID_1." THEN '".$FARE_LABEL_1."'
		    WHEN RESERVED_FLIGHT_ID=".$RESERVED_FLIGHT_ID_2." THEN '".$FARE_LABEL_2."'
			ELSE FARE_LABEL
		END),
		FARE_PRICE_PAID=
		(CASE
		    WHEN RESERVED_FLIGHT_ID=".$RESERVED_FLIGHT_ID_1." THEN ".$FARE_PRICE_PAID_1."
		    WHEN RESERVED_FLIGHT_ID=".$RESERVED_FLIGHT_ID_2." THEN ".$FARE_PRICE_PAID_2."
			ELSE FARE_PRICE_PAID
		END),
		PHONE_NUM=
		(CASE
		    WHEN RESERVED_FLIGHT_ID=".$RESERVED_FLIGHT_ID_1." THEN ".$PHONE_NUM."
		    WHEN RESERVED_FLIGHT_ID=".$RESERVED_FLIGHT_ID_2." THEN ".$PHONE_NUM."
			ELSE PHONE_NUM
		END),
		WIRELESS_CARRIER_ID=
		(CASE
		    WHEN RESERVED_FLIGHT_ID=".$RESERVED_FLIGHT_ID_1." THEN ".$WIRELESS_CARRIER_ID."
		    WHEN RESERVED_FLIGHT_ID=".$RESERVED_FLIGHT_ID_2." THEN ".$WIRELESS_CARRIER_ID."
			ELSE WIRELESS_CARRIER_ID
		END),
		EMAIL=
		(CASE
		    WHEN RESERVED_FLIGHT_ID=".$RESERVED_FLIGHT_ID_1." THEN ".$EMAIL."
		    WHEN RESERVED_FLIGHT_ID=".$RESERVED_FLIGHT_ID_2." THEN ".$EMAIL."
			ELSE EMAIL
		END)";
$result = mysqli_query($conn, $sql);
$error2 = mysqli_error($conn);
if (!$error2) {
	$submissionMessage = "Successfully inserted your new flight info!";
} else {
	$submissionMessage = $error2;
}

$sql = "SELECT COUNT(*) FROM RESERVED_FLIGHTS WHERE CONFIRMATION_NUM='".$CONFIRMATION_NUM."' AND FIRST_NAME='".$FIRST_NAME."' AND LAST_NAME='".$LAST_NAME."'";
if ($res = $db->query($sql)) {
	if ($res->fetchColumn() > 0) {
		$flightCount = 0;
		$sql = "SELECT RF.*,UF.*,A.AIRPORT_NAME AS DEPART_AIRPORT_NAME,B.AIRPORT_NAME AS ARRIVE_AIRPORT_NAME 
				FROM RESERVED_FLIGHTS AS RF 
				LEFT JOIN UPCOMING_FLIGHTS AS UF ON UF.UPCOMING_FLIGHT_ID=RF.UPCOMING_FLIGHT_ID 
				LEFT JOIN AIRPORTS AS A ON A.AIRPORT_CODE=UF.DEPART_AIRPORT_CODE 
				LEFT JOIN AIRPORTS AS B ON B.AIRPORT_CODE=UF.ARRIVE_AIRPORT_CODE 
				WHERE RF.CONFIRMATION_NUM='".$CONFIRMATION_NUM."' AND RF.FIRST_NAME='".$FIRST_NAME."' AND RF.LAST_NAME='".$LAST_NAME."' 
				ORDER BY UF.DEPART_DATE_TIME ASC";
		foreach ($db->query($sql) as $row) {
			$flightCount++;
			if($flightCount == 1) {
				$upcomingFlightId1 = $row['UPCOMING_FLIGHT_ID'];
				$departureDate1 = $row['DEPART_DATE'];
				$flightNum1 = $row['FLIGHT_NUM'];
				$departureCity1 = $row['DEPART_AIRPORT_NAME'];
				$departureTime1 = $row['DEPART_TIME'];
				$arrivalCity1 = $row['ARRIVE_AIRPORT_NAME'];
				$arrivalTime1 = $row['ARRIVE_TIME'];
				$fareType1 = $row['FARE_TYPE'];
				$fareLabel1 = $row['FARE_LABEL'];
				$farePrice1 = $row['FARE_PRICE'];
			} elseif($flightCount == 2) {
				$upcomingFlightId2 = $row['UPCOMING_FLIGHT_ID'];
				$departureDate2 = $row['DEPART_DATE'];
				$flightNum2 = $row['FLIGHT_NUM'];
				$departureCity2 = $row['DEPART_AIRPORT_NAME'];
				$departureTime2 = $row['DEPART_TIME'];
				$arrivalCity2 = $row['ARRIVE_AIRPORT_NAME'];
				$arrivalTime2 = $row['ARRIVE_TIME'];
				$fareType2 = $row['FARE_TYPE'];
				$fareLabel2 = $row['FARE_LABEL'];
				$farePrice2 = $row['FARE_PRICE'];
			}
		}
?>
		<div class="main">
			<form name="swform">
	    		<h1><span>SW</span> <lable> FARE REDUCER </lable> </h1>
	    		<div class="inset">
	    		<p id="newresults">
	    		<?php
		    		if($flightCount == 2) {
		    			echo $submissionMessage."<br><br>";
		    			echo "CONFIRMATION # ".$CONFIRMATION_NUM."<br>";
						echo $FIRST_NAME." ".$LAST_NAME."<br><br>";
						
						$tempDate = strtotime($departureDate1);
						echo "Departure Date : ".date('D, M d, Y', $tempDate)."<br>";
						$tempDate = strtotime($departureTime1);
						echo "Depart: ".$departureCity1." (".date('h:i A', $tempDate).")<br>";
						$tempDate = strtotime($arrivalTime1);
						echo "Arrive: ".$arrivalCity1." (".date('h:i A', $tempDate).")<br>";
						echo "Fare Type : ".$fareType1."<br>";
						echo "Flight # ".$flightNum1."<br>";
						echo $fareLabel1." ".$farePrice1."<br><br>";
						
						$tempDate = strtotime($departureDate2);
						echo "Departure Date : ".date('D, M d, Y', $tempDate)."<br>";
						$tempDate = strtotime($departureTime2);
						echo "Depart: ".$departureCity2." (".date('h:i A', $tempDate).")<br>";
						$tempDate = strtotime($arrivalTime2);
						echo "Arrive: ".$arrivalCity2." (".date('h:i A', $tempDate).")<br>";
						echo "Fare Type : ".$fareType2."<br>";
						echo "Flight # ".$flightNum2."<br>";
						echo $fareLabel2." ".$farePrice2."<br><br>";

						echo "Mobile Alert : ".$EMAIL."<br>";
					} elseif($flightCount == 1) {
						echo $submissionMessage."<br><br>";
		    			echo "CONFIRMATION # ".$CONFIRMATION_NUM."<br>";
						echo $FIRST_NAME." ".$LAST_NAME."<br><br>";
						
						$tempDate = strtotime($departureDate1);
						echo "Departure Date : ".date('D, M d, Y', $tempDate)."<br>";
						$tempDate = strtotime($departureTime1);
						echo "Depart: ".$departureCity1." (".date('h:i A', $tempDate).")<br>";
						$tempDate = strtotime($arrivalTime1);
						echo "Arrive: ".$arrivalCity1." (".date('h:i A', $tempDate).")<br>";
						echo "Fare Type : ".$fareType1."<br>";
						echo "Flight # ".$flightNum1."<br>";
						echo $fareLabel1." ".$farePrice1."<br><br>";

						echo "Mobile Alert : ".$EMAIL."<br>";
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
	    		
				</p>
				</div>
	 	 
				<p class="p-container">
					<input type="button" value="HOME" onclick="goHome();">
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