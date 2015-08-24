<?php

/*
	This is the index file of our simple website.
	It routes requets to the appropriate controllers
*/
error_reporting(0);
require_once "includes/main.php";

try {

	if($_GET['CONFIRMATION_NUM']){
		$c = new UpcomingFlightsController();
	}
	else if($_GET['category']){
		$c = new CategoryController();
	}
	else if(empty($_GET)){
		$c = new HomeController();
	}
	else throw new Exception('Wrong page!');
	
	$c->handleRequest();
}
catch(Exception $e) {
	// Display the error page using the "render()" helper function:
	render('error',array('message'=>$e->getMessage()));
}

?>