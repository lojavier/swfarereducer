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
$DEPART_DATE_1 =		$_POST['DEPART_DATE_1'];
$DEPART_TIME_1 =		$_POST['DEPART_TIME_1'];
$ARRIVE_TIME_1 =		$_POST['ARRIVE_TIME_1'];
$DEPART_AIRPORT_CITY_1 =$_POST['DEPART_AIRPORT_CITY_1'];
$ARRIVE_AIRPORT_CITY_1 =$_POST['ARRIVE_AIRPORT_CITY_1'];
$FARE_TYPE_1 =			$_POST['FARE_TYPE_1'];
$FARE_LABEL_1 = 		$_POST['FARE_LABEL_1'];
$FARE_PRICE_1 = 		$_POST['FARE_PRICE_1'];
$FLIGHT_NUM_1 =			$_POST['FLIGHT_NUM_1'];

$DEPART_DATE_2 =		$_POST['DEPART_DATE_2'];
$DEPART_TIME_2 =		$_POST['DEPART_TIME_2'];
$ARRIVE_TIME_2 =		$_POST['ARRIVE_TIME_2'];
$DEPART_AIRPORT_CITY_2 =$_POST['DEPART_AIRPORT_CITY_2'];
$ARRIVE_AIRPORT_CITY_2 =$_POST['ARRIVE_AIRPORT_CITY_2'];
$FARE_TYPE_2 =			$_POST['FARE_TYPE_2'];
$FARE_LABEL_2 = 		$_POST['FARE_LABEL_2'];
$FARE_PRICE_2 = 		$_POST['FARE_PRICE_2'];
$FLIGHT_NUM_2 =			$_POST['FLIGHT_NUM_2'];

$PHONE_NUM =			$_POST['PHONE_NUM'];
$WIRELESS_CARRIER_ID =	$_POST['WIRELESS_CARRIER_ID'];

$sql = "SELECT CARRIER_TEXT_EMAIL FROM WIRELESS_CARRIERS WHERE WIRELESS_CARRIER_ID=".$WIRELESS_CARRIER_ID;
try {
	$res = $db->query($sql);
	foreach ($db->query($sql) as $row) {
		$EMAIL = $PHONE_NUM.$row['CARRIER_TEXT_EMAIL'];
	}
}
catch(PDOException $e)
{
    $submissionMessage = $e->getMessage();
}
$sql = "SELECT UF.*,A.AIRPORT_NAME as DEPART_AIRPORT_NAME,B.AIRPORT_NAME as ARRIVE_AIRPORT_NAME FROM UPCOMING_FLIGHTS AS UF LEFT JOIN AIRPORTS as A ON A.AIRPORT_CODE=UF.DEPART_AIRPORT_CODE LEFT JOIN AIRPORTS as B ON B.AIRPORT_CODE=UF.ARRIVE_AIRPORT_CODE WHERE UF.CONFIRMATION_NUM='".$CONFIRMATION_NUM."' AND UF.FIRST_NAME='".$FIRST_NAME."' AND UF.LAST_NAME='".$LAST_NAME."' ORDER BY UF.DEPART_DATE ASC";
$sql = "SELECT AIRPORT_CODE as DEPART_AIRPORT_CODE_1, AIRPORT_CODE as ARRIVE_AIRPORT_CODE_1 FROM AIRPORTS WHERE AIRPORT_NAME=".$DEPART_AIRPORT_CODE;
try {
	$res = $db->query($sql);
	foreach ($db->query($sql) as $row) {
		$EMAIL = $PHONE_NUM.$row['CARRIER_TEXT_EMAIL'];
	}
}
catch(PDOException $e)
{
    $submissionMessage = $e->getMessage();
}

if(isset($DEPART_DATE_1) && isset($DEPART_DATE_2)) {
	$sql = "INSERT INTO UPCOMING_FLIGHTS (CONFIRMATION_NUM,FIRST_NAME,LAST_NAME,EMAIL,DEPART_AIRPORT_CODE,ARRIVE_AIRPORT_CODE,DEPART_DATE,DEPART_TIME,ARRIVE_TIME,FLIGHT_NUM,FARE_LABEL,FARE_PRICE,FARE_TYPE) VALUES 
	('".$CONFIRMATION_NUM."','".$FIRST_NAME."','".$LAST_NAME."','".$EMAIL."','".$DEPART_AIRPORT_CODE_1."','".$ARRIVE_AIRPORT_CODE_1."','".$DEPART_DATE_1."','".$DEPART_TIME_1."','".$ARRIVE_TIME_1."','".$FLIGHT_NUM_1."','".$FARE_LABEL_1."','".$FARE_PRICE_1."','".$FARE_TYPE_1."'),
	('".$CONFIRMATION_NUM."','".$FIRST_NAME."','".$LAST_NAME."','".$EMAIL."','".$DEPART_AIRPORT_CODE_2."','".$ARRIVE_AIRPORT_CODE_2."','".$DEPART_DATE_2."','".$DEPART_TIME_2."','".$ARRIVE_TIME_2."','".$FLIGHT_NUM_2."','".$FARE_LABEL_2."','".$FARE_PRICE_2."','".$FARE_TYPE_2."')";
} elseif(isset($DEPART_DATE_1) && !isset($DEPART_DATE_2)) {
	$sql = "INSERT INTO UPCOMING_FLIGHTS (CONFIRMATION_NUM,FIRST_NAME,LAST_NAME,EMAIL,DEPART_AIRPORT_CODE,ARRIVE_AIRPORT_CODE,DEPART_DATE,DEPART_TIME,ARRIVE_TIME,FLIGHT_NUM,FARE_LABEL,FARE_PRICE,FARE_TYPE) VALUES 
	('".$CONFIRMATION_NUM."','".$FIRST_NAME."','".$LAST_NAME."','".$EMAIL."','".$DEPART_AIRPORT_CODE_1."','".$ARRIVE_AIRPORT_CODE_1."','".$DEPART_DATE_1."','".$DEPART_TIME_1."','".$ARRIVE_TIME_1."','".$FLIGHT_NUM_1."','".$FARE_LABEL_1."','".$FARE_PRICE_1."','".$FARE_TYPE_1."')";
}
try {
	$stmt = $db->prepare($sql);
    $stmt->execute();
    $submissionMessage = "Successfully inserted your new flight info!";
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
						
						echo "Departure Date : ".$departureDate1."<br>";
						echo "Depart: ".$departureCity1." (".$departureTime1.")<br>";
						echo "Arrive: ".$arrivalCity1." (".$arrivalTime1.")<br>";
						echo "Fare Type : ".$fareType1."<br>";
						echo "Flight # ".$flightNum1."<br>";
						echo $fareLabel1." ".$farePrice1."<br><br>";
						
						echo "Departure Date : ".$departureDate2."<br>";
						echo "Depart: ".$departureCity2." (".$departureTime2.")<br>";
						echo "Arrive: ".$arrivalCity2." (".$arrivalTime2.")<br>";
						echo "Fare Type : ".$fareType2."<br>";
						echo "Flight # ".$flightNum2."<br>";
						echo $fareLabel2." ".$farePrice2."<br><br>";

						echo "Mobile Alert : ".$EMAIL."<br>";
					} elseif($flightCount == 1) {
						echo $submissionMessage."<br><br>";
		    			echo "CONFIRMATION # ".$CONFIRMATION_NUM."<br>";
						echo $FIRST_NAME." ".$LAST_NAME."<br><br>";
						
						echo "Departure Date : ".$departureDate1."<br>";
						echo "Depart: ".$departureCity1." (".$departureTime1.")<br>";
						echo "Arrive: ".$arrivalCity1." (".$arrivalTime1.")<br>";
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