/*****************************************************************************
 * FILE:      Tethys App Library Module
 * DATE:      6 September 2014
 * AUTHOR:    Nathan Swain
 * COPYRIGHT: (c) 2014 Brigham Young University
 * LICENSE:   BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var TETHYS_APPS_LIBRARY = (function() {
	// Wrap the library in a package function
	"use strict"; // And enable strict mode for this library

	/************************************************************************
 	*                      MODULE LEVEL / GLOBAL VARIABLES
 	*************************************************************************/
 	var public_interface,   // The public interface object that is returned by the module
 	    msnry,              // Global masonry object
 	    app_list_container, // Container with the app items in it
 	    apps_library_url,    // App library url
 	    app_item_selector;  // App item selector

	/************************************************************************
 	*                    PRIVATE FUNCTION DECLARATIONS
 	*************************************************************************/
 	var app_theme_effects, app_exit_handler, hex_to_rgb, launch_app;


 	/************************************************************************
 	*                    PRIVATE FUNCTION IMPLEMENTATIONS
 	*************************************************************************/

 	launch_app = function(element, url) {
 	    // Declare variables
 	    var redirect_delay, transition_duration, transition_duration_string, secondary_margin_bottom;

 	    // Assign variables
 	    transition_duration = 0.4; // seconds
 	    redirect_delay = transition_duration * 1000; // milliseconds
 	    transition_duration_string = transition_duration.toString() + 's';

 	    secondary_margin_bottom = parseInt($('.tethys-secondary-header').css('margin-bottom')) + 300;


 	    // Delay loading app to allow transition
        setTimeout(function(){
          // Redirect to app home page
          window.location = url;
        }, redirect_delay);

        // Hide the headers
        $('.header-wrapper').addClass('with-transition');
        $('.tethys-secondary-header').addClass('with-transition');

        // Hide the headers
        $('.header-wrapper').removeClass('show');
        $('.tethys-secondary-header').removeClass('show');

        // Drop the curtain
        $('#app-library-curtain').addClass('show');
 	};

 	// Handle the app exit transitions in the app
 	app_exit_handler = function() {
 	    // Declare vars
 	    var  referrer_no_protocol, referrer_no_host, transition_duration, transition_duration_string;

 	    // Define transition timing
 	    transition_duration = 0.4; // seconds
 	    transition_duration_string = transition_duration.toString() + 's';

 	    // Get the referrer url and strip off protocol
 	    referrer_no_protocol = document.referrer.split('//')[1];

        // Check if referrer exists and it contains our host
 	    if (referrer_no_protocol && referrer_no_protocol.contains(location.host)) {
            referrer_no_host = referrer_no_protocol.replace(location.host, '');

            // If the referrer is not the apps library url but apps library url is included in the referrer
            // then it is likely we exited from an app
            if ( referrer_no_host !== apps_library_url && referrer_no_host.contains(apps_library_url) ) {
                // Do the opposite of the launch app method (i.e.: have headers hidden and slide in)
                $('.header-wrapper').addClass('with-transition');
                $('.tethys-secondary-header').addClass('with-transition');
            }
 	    }

 	    // Always show headers
 	    $('.header-wrapper').addClass('show');
 	    $('.tethys-secondary-header').addClass('show');
 	};

 	hex_to_rgb = function(hex) {
        var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    };

 	// Apply app theme effects to app icon
 	app_theme_effects = function() {
 	    var app_item_selector;

 	    //app_item_selector = '.app-container .color-effect';
 	    app_item_selector = '.app-container';

 	    $(app_item_selector).each(function() {
            var alpha, theme_color_rgb, tint_string;
            alpha = 0.5;

            theme_color_rgb = hex_to_rgb($(this).attr('data-app-theme-color'));
            tint_string = 'rgba(' + theme_color_rgb.r + ',' + theme_color_rgb.g + ',' + theme_color_rgb.b + ',' + alpha + ')';

            // Apply theme effects
            $(this).css('background-color', tint_string);

            console.log(tint_string);
 	    });

 	};

	/************************************************************************
 	*                        DEFINE PUBLIC INTERFACE
 	*************************************************************************/
	/*
	 * Library object that contains public facing functions of the package.
	 * This is the object that is returned by the library wrapper function.
	 * See below.
	 * NOTE: The functions in the public interface have access to the private
	 * functions of the library because of JavaScript function scope.
	 */
	 public_interface = {
	     launch_app: launch_app
	 };

	/************************************************************************
 	*                  INITIALIZATION / CONSTRUCTOR
 	*************************************************************************/

	// Initialization: jQuery function that gets called when
	// the DOM tree finishes loading
	$(function() {
	    // Add a contains method to the String prototype
	    if ( !String.prototype.contains ) {
            String.prototype.contains = function() {
                return String.prototype.indexOf.apply( this, arguments ) !== -1;
            };
        }

	    // Get a handle on the app items container
	    app_list_container = document.getElementById('app-list');
	    app_item_selector = '.app-container';
	    apps_library_url = '/apps/';

	    // Apply app theme effects
	    //app_theme_effects();

	    // The Tethys apps library page uses masonry.js to accomplish the Pinterest-like stacking of the app icons
	    // Initialize the msnry object if there are any apps in the list.
	    if ( $(app_item_selector).length > 0 ) {
          msnry = new Masonry( app_list_container, {
            // options
            columnWidth: 240,
            itemSelector: app_item_selector
          });

          // If the app icon images take some time to load, it may mess up the masonry formatting. This modules uses the
          // imagesloaded.js project to reformat the masonry after all the images have loaded.
          imagesLoaded( app_list_container, function() {
            msnry.layout();
          });
        }

        // Check for app exit
        app_exit_handler();
	});

	return public_interface;

}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed, returning the public interface object.