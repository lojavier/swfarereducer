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
	if ($res->fetchColumn() > 0) {
		$flightCount = 0;
		$sql = "SELECT * FROM SWFAREREDUCERDB.UPCOMING_FLIGHTS WHERE CONFIRMATION_NUM='".$CONFIRMATION_NUM."' AND FIRST_NAME='".$FIRST_NAME."' AND LAST_NAME='".$LAST_NAME."'";
		foreach ($db->query($sql) as $row) {
			$flightCount++;
			if($flightCount == 1) {
				$departureDate1 = $row['DEPART_DATE'];
				$flightNum1 = $row['FLIGHT_NUM'];
				$departureCity1 = $row['DEPART_AIRPORT_CODE'];
				$departureTime1 = $row['DEPART_TIME'];
				$arrivalCity1 = $row['ARRIVE_AIRPORT_CODE'];
				$arrivalTime1 = $row['ARRIVE_TIME'];
				$fareType1 = $row['FARE_TYPE'];
				$farePrice1 = $row['FARE_PRICE'];
			} elseif($flightCount == 2) {
				$departureDate2 = $row['DEPART_DATE'];
				$flightNum2 = $row['FLIGHT_NUM'];
				$departureCity2 = $row['DEPART_AIRPORT_CODE'];
				$departureTime2 = $row['DEPART_TIME'];
				$arrivalCity2 = $row['ARRIVE_AIRPORT_CODE'];
				$arrivalTime2 = $row['ARRIVE_TIME'];
				$fareType2 = $row['FARE_TYPE'];
				$farePrice2 = $row['FARE_PRICE'];
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
						
						echo "Departure Date : ".$departureDate1."<br>";
						echo "Depart: ".$departureCity1." (".$departureTime1.")<br>";
						echo "Arrive: ".$arrivalCity1." (".$arrivalTime1.")<br>";
						echo "Fare Type : ".$fareType1."<br>";
						echo "Flight # ".$flightNum1."<br>";
				?>
						<input type="radio" name="FARE_LABEL_1" value="DOLLARS">&nbsp;DOLLARS&nbsp;
						<input type="radio" name="FARE_LABEL_1" value="POINTS">&nbsp;POINTS&nbsp;
						<input type="text" name="FARE_PRICE_1" style="width:35%;"> <br>
				<?php
						if( strstr($flightCount, "2") ) {
							echo "Departure Date : ".$departureDate2."<br>";
							echo "Depart: ".$departureCity2." (".$departureTime2.")<br>";
							echo "Arrive: ".$arrivalCity2." (".$arrivalTime2.")<br>";
							echo "Fare Type : ".$fareType2."<br>";
							echo "Flight # ".$flightNum2."<br>";
				?>
							<input type="radio" name="FARE_LABEL_2" value="DOLLARS">&nbsp;DOLLARS&nbsp;
							<input type="radio" name="FARE_LABEL_2" value="POINTS">&nbsp;POINTS&nbsp;
							<input type="text" name="FARE_PRICE_2" style="width:35%;"> <br>
				<?php
						}
					} elseif($flightCount == 1) {
		    			echo "CONFIRMATION # ".$CONFIRMATION_NUM."<br>";
						echo $FIRST_NAME." ".$LAST_NAME."<br><br>";
						
						echo "Departure Date : ".$departureDate1."<br>";
						echo "Depart: ".$departureCity1." (".$departureTime1.")<br>";
						echo "Arrive: ".$arrivalCity1." (".$arrivalTime1.")<br>";
						echo "Fare Type : ".$fareType1."<br>";
						echo "Flight # ".$flightNum1."<br>";
				?>
						<input type="radio" name="FARE_LABEL_1" value="DOLLARS">&nbsp;DOLLARS&nbsp;
						<input type="radio" name="FARE_LABEL_1" value="POINTS">&nbsp;POINTS&nbsp;
						<input type="text" name="FARE_PRICE_1" style="width:35%;"> <br>
				<?php
					} elseif($flightCount < 1) {
						echo "ERROR <br>";
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
	} elseif ($res->fetchColumn() < 1) {
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
