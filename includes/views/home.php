<?php render('_header',array('title'=>$title))?>

<div>
	<form method="POST" action="index.php">
		<!-- <label for="fname" class="ui-hidden-accessible">Firstname</label> -->
		<input type="text" name="confnum" id="confnum" required="required" placeholder="CONFIRMATION #">
		<input type="text" name="fname" id="fname" required="required" placeholder="FIRST NAME">
		<input type="text" name="lname" id="lname" required="required" placeholder="LAST NAME">
		<input type="submit" value="CONTINUE">
	</form>
</div>

<p>This is a website application intended to notify travelers of SW fares for current reservations and/or future reservations.</p>
<p>Submit the information above to start receiving alerts about drop in SW fares.</p>

<ul data-role="listview" data-inset="true" data-theme="c" data-dividertheme="b">
    <li data-role="list-divider">Choose a flight service</li>
    <?php render($content) ?>
</ul>

<?php render('_footer')?>