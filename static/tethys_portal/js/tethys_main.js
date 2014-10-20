/*****************************************************************************
 * FILE:    tethys_apps.js
 * DATE:    5 November 2013
 * AUTHOR: Nathan R. Swain
 * COPYRIGHT: (c) 2013 Brigham Young University
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var CIWATER_THEME = (function() {
	// Wrap the library in a package function
	"use strict"; // And enable strict mode for this library

	/************************************************************************
 	*                      MODULE LEVEL / GLOBAL VARIABLES
 	*************************************************************************/
 	var public_interface,				// Object returned by the module
 	    HERO_WAVE_INITIAL_TOP,
 	    HERO_DROPS_INITIAL_TOP,
 	    HERO_DROPS_INITIAL_LEFT,
 	    FORM_TRIGGER_WIDTH,
 	    SECONDARY_TRIGGER_WIDTH,
 	    TAB_BAR_TRIGGER_WIDTH;



	/************************************************************************
 	*                    PRIVATE FUNCTION DECLARATIONS
 	*************************************************************************/
 	// Date picker private methods
 	var hide_menu, move_secondary_buttons_ify, move_secondary_context_ify, parallax,
 	    remove_empty_elements, toggle_menu, unhorizontalify_forms;

 	hide_menu = function() {
 		// Used to toggle the user menu without inputs
		toggle_menu('#user-profile', '#user-dropdown-toggle', '#user-dropdown-menu');
 	};

 	move_secondary_buttons_ify = function() {
 		// Move buttons from secondary content area to "tab bar"
 		// when the secondary content is not visible
 		if (window.innerWidth <= SECONDARY_TRIGGER_WIDTH) {
 			$('.secondary .module-narrow .nav .btn').each(function() {
 				$(this).appendTo('.wrapper .btn-group.actions').wrap('<li></li>');
 			});
 		}
 	};

 	move_secondary_context_ify = function() {
 		// Move context information (organization and group headings)
 		// from secondary area to primary area when secondary is not
 		// visible
 		if (window.innerWidth <= SECONDARY_TRIGGER_WIDTH) {
 			$('.secondary .context-info').each(function() {
 				$(this).prependTo('.primary .module');
 			});
 		} else {
 			$('.primary .context-info').each(function() {
 				$(this).prependTo('.secondary');
 			});
 		}
 	};

 	parallax = function() {
 		// Here is where all the magic happens for the parallax scrolling
 		// on the home-page
 		if ($(document).find('#home-page').length > 0) {
	 		// Constants
	 		var HERO_MESSAGE_INITIAL_TOP = 125,
		 			HERO_MESSAGE_PARALLAX_RATE = 0.5,
		 			HERO_WAVE_PARALLAX_RATE = 0.25,
		 			HERO_DROPS_PARALLAX_TOP_RATE = -0.05,
		 			HERO_DROPS_PARALLAX_LEFT_RATE = 0.25,
		 			HERO_IMG_ROTATION_RATE = 0.02;

	 		// Variable declarations
	 		var get_started,
	 			get_started_background,
	 			get_started_in,
	 			header_height,
	 			hero_message,
	 			hero_float_img_wave,
	 			hero_float_img_drops,
	 			hero_in,
	 			scroll_position;

	 		// Get scroll position
	 		scroll_position = $(window).scrollTop();
	 		header_height = $('.masthead').outerHeight();

	 		// Get hero message
	 		hero_message = $('.hero-message');
	 		hero_float_img_wave = $('.hero .bucket .float-image.wave');
	 		hero_float_img_drops = $('.hero .bucket .float-image.drops');
	 		get_started_background = $('.get-started-background');

	 		// Determine what's in
	 		hero_in = (scroll_position < ($('.blurb').position().top - header_height));
	 		get_started_in = (scroll_position >= ($('.get-started').position().top - header_height - $(window).height()));

	 		if (hero_in) {
	 			var hero_message_position,
	 			    hero_wave_position,
	 			    hero_drops_top,
	 			    hero_drops_left,
	 			    hero_img_rotation;

	 			// Calculate position
	 			hero_message_position = (HERO_MESSAGE_PARALLAX_RATE * scroll_position) + (HERO_MESSAGE_INITIAL_TOP);
	 			hero_wave_position =  HERO_WAVE_INITIAL_TOP - (HERO_WAVE_PARALLAX_RATE * scroll_position);
	 			hero_drops_top = HERO_DROPS_INITIAL_TOP - (HERO_DROPS_PARALLAX_TOP_RATE * scroll_position);
	 			hero_drops_left = HERO_DROPS_INITIAL_LEFT + (HERO_DROPS_PARALLAX_LEFT_RATE * scroll_position);
	 			hero_img_rotation =  HERO_IMG_ROTATION_RATE * scroll_position;

	 			// Set styles
	 			hero_message.css('top', hero_message_position);
	 			hero_float_img_wave.css('top', hero_wave_position);
	 			hero_float_img_drops.css('top', hero_drops_top);
	 			hero_float_img_drops.css('left', hero_drops_left);
	 			hero_float_img_wave.css('-webkit-transform', 'rotate(' + hero_img_rotation + 'deg)');
	 			hero_float_img_wave.css('-moz-transform', 'rotate(' + hero_img_rotation + 'deg)');
	 			hero_float_img_wave.css('-o-transform', 'rotate(' + hero_img_rotation + 'deg)');
	 			hero_float_img_wave.css('-ms-transform', 'rotate(' + hero_img_rotation + 'deg)');
	 			hero_float_img_wave.css('transform', 'rotate(' + hero_img_rotation + 'deg)');

	 			// Unlight "Log In" action button
	 			if ($('.header-action').hasClass('lit')) {
	 				$('.header-action').removeClass('lit');
	 			}
	 		}
	 		else {
	 			// Light up the "Log In" actino button
	 			if (!$('.header-action').hasClass('lit')) {
	 				$('.header-action').addClass('lit');
	 			}
	 		}

	 		if (get_started_in) {
	 			get_started_background.show();
	 		} else {
	 			get_started_background.hide();
	 		}
 		}
 	};

 	remove_empty_elements = function() {
 		// Removes the header and "tab bar" when they are empty
 		if (window.innerWidth <= TAB_BAR_TRIGGER_WIDTH) {
 			var actions_children, header_children;

 			actions_children = $('.btn-group.actions').children();
 			header_children = $('.page-header').children();

 			// Remove empty tab bar
 			if (actions_children.length <= 0) {
 				$('.btn-group.actions').remove();
 			}

 			// Remove empty header
 			if (header_children.length <= 0) {
 				$('.page-header').remove();
 			}
 		}
 	};

 	toggle_menu = function(user, toggle, menu_id) {
 		// Toggle the visibility of the user menu
 		var visibility,
 		    left, right, width, right_string,
 		    top, height, menu_top, masthead_height, top_string,
 		    user_width, menu_width, menu_width_string,
 		    invisible_div,
 		    scroll_position;

 		// Get current visibility
 		visibility = $(menu_id).css('visibility');

 		// Get invisible div
 		invisible_div = $('.transparent-div');

 		// Get right extent of toggle
 		left = $(toggle).offset().left;
 		width = $(toggle).outerWidth();
 		right = $(window).width() - (left + width);

 		right_string = right.toString() + 'px';

 		// Get top extent of toggle
 		masthead_height = $('.masthead').outerHeight();

 		// top is the offset from the top of masthead to the toggle link
 		top = 20;

 		// Handle case when header menu wraps prior to mobile menu switch
 		if (masthead_height >= 160) { top = 100; }

 		scroll_position = $(window).scrollTop();
 		height = $(toggle).outerHeight();
 		menu_top = top + height + 5;

 		console.log('top: ', top);
 		console.log('height: ', height);
 		console.log('menu_top: ', menu_top);

 		top_string = menu_top.toString() + 'px';

 		// Get width extent for menu
 		user_width = $(user).outerWidth();
 		menu_width = user_width + width;

 		menu_width_string = menu_width.toString() + 'px';

 		// Toggle visibility
 		if (visibility === 'hidden') {
 			// Set top and right property
 			$(menu_id).css({'right': right_string,
 						    'top': top_string,
 						    'width': menu_width_string });


 			// Show the menu
 			$(menu_id).css('visibility', 'visible');
 			$(invisible_div).show();

 			// Light up toggle
 			$(toggle).toggleClass('lit');

 		} else {
 			$(menu_id).css('visibility', 'hidden');
 			$(invisible_div).hide();

 			// Darken toggle
 			$(toggle).toggleClass('lit');
 		}
 	};

 	unhorizontalify_forms = function() {
 		// Fix forms for small screens by removing the
 		// bootstrap form-horizontal class
 		if (window.innerWidth <= FORM_TRIGGER_WIDTH) {

			$('.form-horizontal').each(function(){
				$(this).removeClass('form-horizontal');
			});
		}
 	};

	/************************************************************************
 	*                            TOP LEVEL CODE
 	*************************************************************************/
	/*
	 * Library object that contains public facing functions of the package.
	 */
	public_interface = {
		toggle_menu: toggle_menu,
		hide_menu: hide_menu
	};


	// Initialization: jQuery function that gets called when
	// the DOM tree finishes loading
	$(function() {

		// Initialize globals
		FORM_TRIGGER_WIDTH = 1150;
		SECONDARY_TRIGGER_WIDTH = 700;
		TAB_BAR_TRIGGER_WIDTH = 950;

		// Scroll to top of window to prevent... issues
		$(window).scrollTop(0);

		// Bind parallax on scroll and resize events
		$(window).on('scroll', parallax);
		$(window).on('resize', parallax);

		// Hide mobile navs on window resize to avoid... complications
		$(window).on('resize', function() {
			$('.mobile-nav').each(function(){
				if ($(this).hasClass('in')) {
					$(this).toggleClass('in');
				}
			});
		});

		// Bind to the click events on the mobile nav buttons
		$('.mobile-nav-button.mobile-links').on('click', function() {
			$('.mobile-nav.mobile-nav-links').toggleClass('in');

			if ($('.mobile-nav.mobile-user-links').hasClass('in')) {
				$('.mobile-nav.mobile-user-links').toggleClass('in');
			}
		});

		$('.mobile-nav-button.mobile-user').on('click', function() {
			$('.mobile-nav.mobile-user-links').toggleClass('in');

			if ($('.mobile-nav.mobile-nav-links').hasClass('in')) {
				$('.mobile-nav.mobile-nav-links').toggleClass('in');
			}
		});

		// Set initial values of float image
		if ($(document).find('#home-page').length > 0) {
			HERO_WAVE_INITIAL_TOP = $('.hero .bucket .float-image.wave').position().top;
			HERO_DROPS_INITIAL_TOP = $('.hero .bucket .float-image.drops').position().top;
			HERO_DROPS_INITIAL_LEFT = $('.hero .bucket .float-image.drops').position().left;
		}

		// DOM Modifications for mobile versions
		unhorizontalify_forms(); // Remove form-horizontal class on forms
		$(window).on('resize', unhorizontalify_forms);

		move_secondary_buttons_ify(); // Move any buttons from the secondary content area
		$(window).on('resize', move_secondary_buttons_ify);

		move_secondary_context_ify(); // Move context information from secondary content
		$(window).on('resize', move_secondary_context_ify);

		remove_empty_elements();
		$(window).on('resize', remove_empty_elements);
	});

	return public_interface;

}()); // End of package wrapper

/*****************************************************************************
 *                      Public Functions
 *****************************************************************************/

function toggle_menu(user, toggle, menu_id) {
	"use strict";

	CIWATER_THEME.toggle_menu(user, toggle, menu_id);
}

function hide_menu() {
	"use strict";

	CIWATER_THEME.hide_menu();
}
