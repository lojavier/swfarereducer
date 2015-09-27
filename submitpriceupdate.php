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
$UPCOMING_FLIGHT_ID_1 = $_POST['UPCOMING_FLIGHT_ID_1'];
$FARE_LABEL_1 = 		$_POST['FARE_LABEL_1'];
$FARE_PRICE_1 = 		$_POST['FARE_PRICE_1'];
$UPCOMING_FLIGHT_ID_2 = $_POST['UPCOMING_FLIGHT_ID_2'];
$FARE_LABEL_2 = 		$_POST['FARE_LABEL_2'];
$FARE_PRICE_2 = 		$_POST['FARE_PRICE_2'];

$sql = "UPDATE UPCOMING_FLIGHTS 
		SET FARE_LABEL=
		(CASE
		    WHEN UPCOMING_FLIGHT_ID=".$UPCOMING_FLIGHT_ID_1." THEN '".$FARE_LABEL_1."'
		    WHEN UPCOMING_FLIGHT_ID=".$UPCOMING_FLIGHT_ID_2." THEN '".$FARE_LABEL_2."'
			ELSE FARE_LABEL
		END),
		FARE_PRICE=
		  (CASE
		    WHEN UPCOMING_FLIGHT_ID=".$UPCOMING_FLIGHT_ID_1." THEN ".$FARE_PRICE_1."
		    WHEN UPCOMING_FLIGHT_ID=".$UPCOMING_FLIGHT_ID_2." THEN ".$FARE_PRICE_2."
			ELSE FARE_PRICE
		  END)";
try {
	$stmt = $db->prepare($sql);
    $stmt->execute();
    $submissionMessage = "Successfully updated your flight prices!";
}
catch(PDOException $e)
{
    $submissionMessage = $e->getMessage();
}

$sql = "SELECT COUNT(*) FROM SWFAREREDUCERDB.UPCOMING_FLIGHTS WHERE CONFIRMATION_NUM='".$CONFIRMATION_NUM."' AND FIRST_NAME='".$FIRST_NAME."' AND LAST_NAME='".$LAST_NAME."'";
if ($res = $db->query($sql)) {
	if ($res->fetchColumn() > 0) {
		$flightCount = 0;
		$sql = "SELECT UF.*,A.AIRPORT_NAME as DEPART_AIRPORT_NAME,B.AIRPORT_NAME as ARRIVE_AIRPORT_NAME FROM UPCOMING_FLIGHTS AS UF LEFT JOIN AIRPORTS as A ON A.AIRPORT_CODE=UF.DEPART_AIRPORT_CODE LEFT JOIN AIRPORTS as B ON B.AIRPORT_CODE=UF.ARRIVE_AIRPORT_CODE WHERE UF.CONFIRMATION_NUM='".$CONFIRMATION_NUM."' AND UF.FIRST_NAME='".$FIRST_NAME."' AND UF.LAST_NAME='".$LAST_NAME."' ORDER BY UF.DEPART_DATE ASC";
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
						echo $fareLabel2." ".$farePrice2."<br>";
					} elseif($flightCount == 1) {
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