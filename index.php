<?php ob_start(); ?>
<!DOCTYPE html>
<html lang="de"><!-- use class="debug" here if you develop a template and want to check-->
<head>
	<meta charset="UTF-8" />
	<meta name="viewport" content="width=device-width, minimum-scale=1.0, maximum-scale=1.0" />
   	<!-- some meta tags, important for SEO"--> 
    <meta name="description" content="SpartanBrew - Automated Home Beer Brewing System" />
    <meta name="keywords" content="spartanbrew, spartan, brew, spartan brew, beer, homebrew, home brew, homebrewing, automation, automate" />
    <meta name="revisit-after" content="7 days" />
    <meta name="robots" content="index,follow" />
	
	<title>SW Fare Reducer</title>
</head>
<!--===============================================================  Logo, social and menu =====================================================================================--> 
<body>
<?php
/*
	This is the index file of our simple website.
	It routes requests to the appropriate controllers
*/

require_once "includes/main.php";

try {

	if($_GET['category']){
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
</body>
</html>