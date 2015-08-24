<?php

/* This controller renders the home page */

class HomeController{
	public function handleRequest(){
		
		// Select all the categories:
		$content = Category::find();

		$upcomingflights = UpcomingFlights::find();
		
		render('home',array(
			'title'		=> 'SW FARE REDUCER',
			'upcomingflights' => $upcomingflights,
			'content'	=> $content
		));
	}
}

?>