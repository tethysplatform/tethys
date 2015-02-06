/*****************************************************************************
 * FILE:      Tethys App Base Module
 * DATE:      6 September 2014
 * AUTHOR:    Nathan Swain
 * COPYRIGHT: (c) 2014 Brigham Young University
 * LICENSE:   BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var TETHYS_APP_BASE = (function() {
	// Wrap the library in a package function
	"use strict"; // And enable strict mode for this library

	/************************************************************************
 	*                      MODULE LEVEL / GLOBAL VARIABLES
 	*************************************************************************/
 	var public_interface,         // The public interface object that is returned by the module
 	    apps_library_url,         // The relative url of the apps library page
 	    app_header_selector,      // String selector for the app header element
 	    app_content_selector,     // String selector for the app content element
 	    wrapper_selector,         // String selector for the app wrapper element
 	    toggle_nav_selector,      // String selector for the toggle nav element
 	    app_navigation_selector,  // String selector for the app navigation element
 	    tethys_nav_cookie_key,    // Key for the tethys apps nav cookie
 	    nav_in_value,             // Value of the nav cookie when nav is in
 	    nav_out_value,            // Value of the nav cookie when nav is out
 	    app_color;                // App color



	/************************************************************************
 	*                    PRIVATE FUNCTION DECLARATIONS
 	*************************************************************************/
 	var apply_content_height, apply_app_color_theme, app_entry_handler, check_responsive,
 	    no_nav_handler, exit_app, toggle_nav;


 	/************************************************************************
 	*                    PRIVATE FUNCTION IMPLEMENTATIONS
 	*************************************************************************/

    // Handle toggling nav effects
 	toggle_nav = function() {
 	    // Add the with-transition class if not present
 	    if ( !$(wrapper_selector).hasClass('with-transition') ) {
 	        $(wrapper_selector).addClass('with-transition');
 	    }

 	    // Toggle the show-nav class
        if ($(wrapper_selector).hasClass('show-nav')) {
            // Do things on Nav Close
            $(wrapper_selector).removeClass('show-nav');
            $(toggle_nav_selector).css('width', '20px');
            $(toggle_nav_selector).css('margin-right', '0');

            // Toggle cookie
            docCookies.setItem(tethys_nav_cookie_key, nav_out_value, null, apps_library_url);

        } else {
            // Do thing on Nav Open
            $(wrapper_selector).addClass('show-nav');
            $(toggle_nav_selector).css('width', '15px');
            $(toggle_nav_selector).css('margin-right', '5px');

            // Toggle cookie
            docCookies.setItem(tethys_nav_cookie_key, nav_in_value, null, apps_library_url);

        }
 	};

 	// Handle the entry entry transitions in the app
 	app_entry_handler = function() {
 	    // Declare vars
 	    var  referrer_no_protocol, referrer_no_host;

 	    // Get the referrer url and strip off protocol
 	    referrer_no_protocol = document.referrer.split('//')[1];

        // Check if referrer exists and it contains our host
 	    if (referrer_no_protocol && referrer_no_protocol.indexOf(location.host) > -1) {
            referrer_no_host = referrer_no_protocol.replace(location.host, '');

            // If the referrer was the app library, add transition classes to create a
            // smooth transition effect on app launch
            if (referrer_no_host === apps_library_url) {
                // Enable the transitions
                $(app_header_selector).addClass('with-transition');
                $(app_content_selector).addClass('with-transition');

                // Remove the nav cookie
 	            docCookies.removeItem(tethys_nav_cookie_key, apps_library_url);
            }
 	    }

        // Add the "show" classes appropriately to show things that are hidden by default
 	    $(app_header_selector).addClass('show-header');
 	    $(app_content_selector).addClass('show-app-content');

 	    // Check the nav cookie
 	    if (docCookies.hasItem(tethys_nav_cookie_key)) {
 	      var nav_cookie_value;

 	      // Read the cookie
 	      nav_cookie_value = docCookies.getItem(tethys_nav_cookie_key);

          if (nav_cookie_value == nav_out_value) {
            $(wrapper_selector).removeClass('show-nav');

          } else if (nav_cookie_value == nav_in_value) {
            $(wrapper_selector).addClass('show-nav');
          }
 	    }
 	};

 	// Handle case when there is no nav present
 	no_nav_handler = function() {
 	    // If no nav present...
        if ( !$(app_navigation_selector).length ) {
            // Hide the nav area
            $('#app-content').css('transition', 'none');
            $(wrapper_selector).removeClass('show-nav');

            // Hide the toggle button and then remove it
            $(toggle_nav_selector).css('display', 'none');
            $(toggle_nav_selector).remove();
        }
 	};

    // Handle changes in app content height
 	apply_content_height = function() {
 	    // Declare variables
 	    var app_actions_height, content_height, header_height, window_height;

 	    // Remove height property on wrapper so our measurement isn't biased
 	    $(wrapper_selector).css('height', 'auto');

        // Measure the content height and the window height for comparison
 	    content_height = parseInt($('#app-content').css('height'));
 	    window_height = window.innerHeight;

        // If the content height is less than the window height...
 	    if (content_height <= window_height) {
 	      // Set the height to 100% so the content fills the window
 	      $(wrapper_selector).css('height', '100%');

 	    } else {
          // Otherwise, set the height to auto so that it overflows appropriately
          $(wrapper_selector).css('height', 'auto');

 	    }
 	};

    // Apply the custom color theme defined by app developer
 	apply_app_color_theme = function() {
 	    // Declare vars
 	    var rgb_parts, rgba_string, alpha;

 	    alpha = 0.5;

 	    // Apply theme to various elements
 	    $('#app-header .tethys-app-header .icon-wrapper img').css('background-color', app_color);
 	    $('#app-navigation .nav li a').css('color', app_color);
 	    $('#app-navigation .nav li.active a').css('background-color', app_color);
 	    $('#app-navigation .nav li.active a').css('color', '#ffffff');

 	    // Parse the rgb string into parts
 	    rgb_parts = app_color.match(/^rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$/i);

 	    // Use the parts to create an rgba string with transparency
 	    if (rgb_parts) {
 	        rgba_string = 'rgba(' + rgb_parts[1] + ', ' + rgb_parts[2] + ', ' + rgb_parts[3] + ', ' + alpha.toString() + ')';
 	        $('#app-content-wrapper #app-content #app-actions').css('background-color', rgba_string);
 	    }
 	};

 	// Check for responsive parameters
 	check_responsive = function() {
        var window_width;

        window_width = window.innerWidth;

        // Hide the nav if less than threshold
        if ( window_width < 900 && $(wrapper_selector).hasClass('show-nav') ) {
          $(wrapper_selector).removeClass('show-nav');
          docCookies.setItem(tethys_nav_cookie_key, nav_out_value, null, apps_library_url);
        }
 	};

    // Apply transition effect to exit button press
 	exit_app = function(url) {
 	    var redirect_delay;

        redirect_delay = 400; // milliseconds

        setTimeout(function(){
          // Remove the nav cookie
 	      docCookies.removeItem(tethys_nav_cookie_key, apps_library_url);

 	      // Redirect to app home page
          window.location = url;
        }, redirect_delay);

        // Add transition classes if necessary
        if ( !$(app_header_selector).hasClass('with-transition') ) {
          $(app_header_selector).addClass('with-transition');
        }

        if ( !$(app_content_selector).hasClass('with-transition') ) {
          $(app_content_selector).addClass('with-transition');
        }

        // Hide by removing "show" classes
        $(app_header_selector).removeClass('show-header');
        $(app_content_selector).removeClass('show-app-content');
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
         toggle_nav: toggle_nav,
         exit_app: exit_app,
     };

	/************************************************************************
 	*                  INITIALIZATION / CONSTRUCTOR
 	*************************************************************************/

	// Initialization: jQuery function that gets called when
	// the DOM tree finishes loading
	$(function() {
	    // Selector globals
	    apps_library_url = '/apps/';
	    app_header_selector = '.tethys-app-header';
 	    app_content_selector = '#app-content';
	    wrapper_selector = '#app-content-wrapper';
	    toggle_nav_selector = '.toggle-nav';
	    app_navigation_selector = '#app-navigation';

	    // Cookie globals
	    tethys_nav_cookie_key = 'tethysappnav';
	    nav_in_value = "a7dfd75f8f41f038258effc6d975cef7";
	    nav_out_value = "3f64a50b313be90cc612d9a0a1debf30";

	    // Style globals
	    app_color = $(app_header_selector).css('background-color');

	    // Apply color styles
	    apply_app_color_theme();

        // Bind toggle_nav to the click event of ".toggle-nav" element
        $(toggle_nav_selector).click(function() {
            public_interface.toggle_nav();
            apply_content_height();
        });

        // Bind to the window resize event
        window.onresize = function() {
          apply_content_height();
          check_responsive();
        }

        // Adjust content height accordingly
	    apply_content_height();

	    // Run no nav handler
	    no_nav_handler();

	    // Run the app entry handler
	    app_entry_handler();

	    // Perform responsive check
	    check_responsive();

	});

	return public_interface;

}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed, returning the public interface object.