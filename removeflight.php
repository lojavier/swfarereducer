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
		function submitFlightRemoval()
		{
			document.swform.action = "submitflightremoval.php";
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
			<form method="POST" name="swform">
	    		<h1><span>SW</span> <lable> FARE REDUCER </lable> </h1>
	    		<div class="inset">
	    		<p id="newresults">
	    		<?php
		    		if($flightCount == 2) {
		    			echo "CONFIRMATION # ".$CONFIRMATION_NUM."<br>";
						echo $FIRST_NAME." ".$LAST_NAME."<br><br>";
				?>
						<div style='position:relative; clear:left; width:100%;'>
							<div style='float:left; zoom:1.5;'>
								<input type='checkbox' name='UPCOMING_FLIGHT_ID_1' value=<?php echo $upcomingFlightId1; ?>>
							</div>
							<div style='float:left; padding-left:10px;'><p id='newresults'>
				<?php
						echo "Departure Date : ".$departureDate1."<br>";
						echo "Depart: ".$departureCity1." (".$departureTime1.")<br>";
						echo "Arrive: ".$arrivalCity1." (".$arrivalTime1.")<br>";
						echo "Fare Type : ".$fareType1."<br>";
						echo "Flight # ".$flightNum1."<br>";
						echo $fareLabel1." ".$farePrice1;
				?>
							</p><br>
							</div>
						</div>
						
						<div style='position:relative; clear:left; width:100%;'>
							<div style='float:left; zoom:1.5;'>
								<input type='checkbox' name='UPCOMING_FLIGHT_ID_2' value=<?php echo $upcomingFlightId2; ?>>
							</div>
							<div style='float:left; padding-left:10px;'><p id='newresults'>
				<?php
							echo "Departure Date : ".$departureDate2."<br>";
							echo "Depart: ".$departureCity2." (".$departureTime2.")<br>";
							echo "Arrive: ".$arrivalCity2." (".$arrivalTime2.")<br>";
							echo "Fare Type : ".$fareType2."<br>";
							echo "Flight # ".$flightNum2."<br>";
							echo $fareLabel2." ".$farePrice2;
				?>
							</p><br>
							</div>
						</div>
				<?php
					} elseif($flightCount == 1) {
		    			echo "CONFIRMATION # ".$CONFIRMATION_NUM."<br>";
						echo $FIRST_NAME." ".$LAST_NAME."<br><br>";
				?>
						<div style='position:relative; clear:left; width:100%;'>
							<div style='float:left; zoom:1.5;'>
								<input type='checkbox' name='UPCOMING_FLIGHT_ID_1' value=<?php echo $upcomingFlightId1; ?>>
							</div>
							<div style='float:left; padding-left:10px;'><p id='newresults'>
				<?php
							echo "Departure Date : ".$departureDate1."<br>";
							echo "Depart: ".$departureCity1." (".$departureTime1.")<br>";
							echo "Arrive: ".$arrivalCity1." (".$arrivalTime1.")<br>";
							echo "Fare Type : ".$fareType1."<br>";
							echo "Flight # ".$flightNum1."<br>";
							echo $fareLabel1." ".$farePrice1;
				?>
							</p><br>
							</div>
						</div>
				<?php
					} elseif($flightCount < 1) {
						echo "ERROR <br>";
					}
				?>
				</p>
				</div>
	 	 		<input type="hidden" name="CONFIRMATION_NUM" value=<?php echo $CONFIRMATION_NUM;?>>
				<input type="hidden" name="FIRST_NAME" value=<?php echo $FIRST_NAME;?>>
				<input type="hidden" name="LAST_NAME" value=<?php echo $LAST_NAME;?>>
				<p class="p-container">
					<input type="submit" value="REMOVE" onclick="submitFlightRemoval();">
				</p>
				<p class="p-container">
					<input type="submit" value="HOME" onclick="goHome();">
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
	    		<?php echo "ERROR: Flight does not exist in our database! <br>"; ?>
				</p>
				</div>
	 	 
				<p class="p-container">
					<input type="submit" value="HOME" onclick="goHome();">
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
