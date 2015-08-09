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
	
	<title>SpartanBrew</title>
			
            
    <link rel="stylesheet" href="css/inuit.css" />
    <link rel="stylesheet" href="css/fluid-grid16-1100px.css" />
    <link rel="stylesheet" href="css/eve-styles.css" />
    <link rel="shortcut icon" href="icon.png" />
    <link rel="apple-touch-icon-precomposed" href="img/icon.png" />
    
    <script src="js/respond-min.js" type="text/javascript"></script>
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js" type="text/javascript"></script>
    <script>window.jQuery || document.write('<script src="scripts/jquery164min.js">\x3C/script>')</script><!--local fallback for JQuery-->
	<script src="js/jquery.flexslider-min.js" type="text/javascript"></script>
    <link rel="stylesheet" href="css/flexslider.css" />
    
    <script type="text/javascript">
		  $(window).load(function() {
			$('.flexslider').flexslider({
				  animation: "slide",<!--you can also choose fade here-->
				  directionNav: true,<!--Attention: if you choose true here, the nav-buttons will also appear in the ticker! -->
				  keyboardNav: true,
				  mousewheel: true
			});
		  });
	</script>
       
            <!--Hide the hr img because of ugly borders in IE7. You can change the color of border-top to display a line -->
            <!--[if lte IE 7]>

                <style>
            		hr { display:block; height:1px; border:0; border-top:1px solid #fff; margin:1em 0; padding:0; }
                    .grid-4{ width:22% }
                </style>
            <![endif]-->

</head>
<!--===============================================================  Logo, social and menu =====================================================================================--> 
<body>
<?php
if (version_compare(PHP_VERSION, '5.3.7', '<')) {
    exit("Sorry, Simple PHP Login does not run on a PHP version smaller than 5.3.7 !");
} else if (version_compare(PHP_VERSION, '5.5.0', '<')) {
    require_once("libraries/password_compatibility_library.php");
}

require_once("config/spartanbrewdb.php");
require_once("classes/Login.php");
//require_once("classes/Registration.php");

$login = new Login();
//$registration = new Registration();

if ($login->isUserLoggedIn() == true) { // ************************************* logged in ******************************************************
	// show potential errors / feedback (from login object)
	if (isset($login)) {
		if ($login->errors) {
			foreach ($login->errors as $error) {
				echo "<script>";
				echo "alert ('$error')";
				echo "</script>";
			}
		}
		if ($login->messages) {
			foreach ($login->messages as $message) {
				echo "<script>";
				echo "alert ('$message')";
				echo "</script>";
			}
		}
	}
	if (isset($registration)) {
		if ($registration->errors) {
			foreach ($registration->errors as $error) {
				echo "<script>";
				echo "alert ('$error')";
				echo "</script>";
			}
		}
		if ($registration->messages) {
			foreach ($registration->messages as $message) {
				echo "<script>";
				echo "alert ('$message')";
				echo "</script>";
			}
		}
	}
	header('Location: home.php');
	exit();
} else { // ************************************* NOT logged in ******************************************************
?>
	<div class="wrapper">	
                    <a href="index.php" id="logo"><img src="img/logo.png" alt="something" />
                      <h1 class="accessibility">SpartanBrew</h1></a>
                   
                   <!--These are just samples, use your own icons. If you use larger ones, make sure too change the css-file to fit them in.
                       Dont´t forget to place your links -->
                    <div class="social">
                    <a href="http://www.facebook.com/profile.php?id=100001520859552" title="facebook"><img src="img/facebook.png" width="20" height="20" alt="facebook"></a>
                    <a href="http://twitter.com/#!/sg_layout" title="twitter"><img src="img/twitter.png" width="20" height="20" alt="twitter"></a>
                    <a href="#" title="linkedin"><img src="img/linkedin.png" width="20" height="20" alt="linkedin"></a>
					<a href="#" title="instagram"><img src="img/instagram.png" width="20" height="20" alt="instagram"></a>
                    </div>
                    
                    <ul id="nav" class="main">
                        <li><a href="#" class="active">Login</a></li>
                        <li><a href="register.php">Register</a></li>
						<li><a href="contact.php">Contact</a></li>
                    </ul>
					   
        </div><!--end of wrapper div-->    
	<div class="clear"></div> 
    
<!--========================================================================== Intro and FlexSlider =====================================================================================-->    

	<div class="wrapper">
 		<div class="grids top">
                <div class="grid-6 grid intro">
                 <h2>Login</h2>
					<form method="post" action="index.php" name="loginform">
						<label>Email address</label> <br>
						<input id="" type="email" name="brewer_email" autofocus required autocomplete="on" tabindex="1"/> <br>
						<label>Password</label> <br>
						<input id="" type="password" name="brewer_password" autocomplete="off" required tabindex="2"/> <br>
						<a href="passwordreset.php">Forgot your password?</a> <br>
						<input id="login_button" type="submit" name="login" value="Login" /> <br>
					</form> <br>
					
					<p>Login to access the database of beers we have available to brew. Also, brewing history and statistics are available 
					to view. <br><br>
					ATTENTION GUESTS! <br>
					email: guest@spartanbrew.net <br>
					password: password</p>
                                        
                 </div><!--end of slogan div-->
 
                 <div class="grid-10 grid"> 
                
					<?php include 'slideshow.php'; ?>
				
				</div><!--end of div grid-10-->
		</div><!--end of div grids-->
		<!--<span class="slidershadow"></span>-->
				
	</div><!--end of div wrapper-->
            
<!--========================================================================== Content Part 1 =====================================================================================-->             

    <div class="wrapper">
    
		<div class="grids">

			<div class="grid-10 grid">
				
						<h2>Header</h2>
						<p>Still in progress.</p>
						
						<p>Still in progress.</p>
					   
						<a class="button" href="#">Download me!</a>

			</div><!--end of grid-10--> 
			
			
			<div class="grid-6 grid grey">
						<h2>This is a quote</h2>
						<p class="quote">"Still in progress."
						<span>SpartanBrew</span></p>
		
			</div>
	   
			
		</div><!--end of grids-->
	   
	</div><!--end of wrapper-->
	
	<hr /> 		

<!--========================================================================== Content Part 2 =====================================================================================-->         
    
	<?php include 'middlecontent.php'; ?>	
		
	<hr /> 
 
<!--========================================================================== Bottom Content  =====================================================================================-->       
		
		<?php include 'bottomcontent.php'; ?>
		
		<!-- <video width="100%" controls preload="auto">
				<source src="vid/solenoid-test.mp4" type="video/mp4">
			</video> -->

<!--========================================================================== Footer =====================================================================================-->     
		<div class="wrapper">
					<div id="footer">
            	
						<?php include 'footer.php';?>
					
                   </div><!--end of footer-->
		   </div><!--end of wrapper-->
    
    
        				<script type="text/javascript"> <!--Outdated browsers warning/message and link to Browser-Update. Comment or delete it if you don´t want to use it-->
						var $buoop = {} 
						$buoop.ol = window.onload; 
						window.onload=function(){ 
						 try {if ($buoop.ol) $buoop.ol();}catch (e) {} 
						 var e = document.createElement("script"); 
						 e.setAttribute("type", "text/javascript"); 
						 e.setAttribute("src", "http://browser-update.org/update.js"); 
						 document.body.appendChild(e); 
						} 
						</script> 
<?php
	// show potential errors / feedback (from login object)
	if (isset($login)) {
		if ($login->errors) {
			foreach ($login->errors as $error) {
				echo "<script>";
				echo "alert ('$error')";
				echo "</script>";
			}
		}
		if ($login->messages) {
			foreach ($login->messages as $message) {
				echo "<script>";
				echo "alert ('$message')";
				echo "</script>";
			}
		}
	}
	if (isset($registration)) {
		if ($registration->errors) {
			foreach ($registration->errors as $error) {
				echo "<script>";
				echo "alert ('$error')";
				echo "</script>";
			}
		}
		if ($registration->messages) {
			foreach ($registration->messages as $message) {
				echo "<script>";
				echo "alert ('$message')";
				echo "</script>";
			}
		}
	}
}
?>
</body>
</html>