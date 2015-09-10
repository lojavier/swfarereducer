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
$con = mysqli_connect("127.0.0.1","root","swfarereducer","SWFAREREDUCERDB");
if (mysqli_connect_errno()) {
    printf("Connect failed: %s\n", mysqli_connect_error());
    exit();
}

$sql = "SELECT * FROM SWFAREREDUCERDB.UPCOMING_FLIGHTS WHERE CONFIRMATION_NUM='".$_POST['CONFIRMATION_NUM']."' AND FIRST_NAME='".$_POST['FIRST_NAME']."' AND LAST_NAME='".$_POST['LAST_NAME']."' ORDER BY DEPART_DATE ASC";
echo $sql;
if ($result = mysqli_query($con, $sql) {
	$row_cnt = mysqli_num_rows($result);
	printf("Result set has %d rows.\n", $row_cnt);
    mysqli_free_result($result);
    mysqli_close($con);
    if($row_cnt == 0) {
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
	}
}
</body>
</html>
