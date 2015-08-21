<?php render('_header',array('title'=>$title))?>

<div>
	<form method="POST" action="index.php">
		<input type="text" name="confirmationNum" id="confirmationNum" required="required" placeholder="CONFIRMATION #">
		<input type="text" name="firstName" id="firstName" required="required" placeholder="FIRST NAME">
		<input type="text" name="lastName" id="lastName" required="required" placeholder="LAST NAME">
		<input type="submit" value="CONTINUE">
	</form>
</div>

<ul data-role="listview" data-inset="true" data-theme="c" data-dividertheme="b">
    <li data-role="list-divider">Upcoming Flights</li>
    <?php render($upcoming_flights) ?>
</ul>

<p>This is a website application intended to notify travelers of SW fares for current reservations and/or future reservations.</p>
<p>Submit the information above to start receiving alerts about drop in SW fares.</p>

<ul data-role="listview" data-inset="true" data-theme="c" data-dividertheme="b">
    <li data-role="list-divider">Categories</li>
    <?php render($content) ?>
</ul>

<?php render('_footer')?>