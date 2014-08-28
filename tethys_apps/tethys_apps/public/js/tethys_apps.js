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

var TETHYS_APPS = (function() {
	// Wrap the library in a package function
	"use strict"; // And enable strict mode for this library
	
	/************************************************************************
 	*                      MODULE LEVEL / GLOBAL VARIABLES
 	*************************************************************************/
 	var public_interface;				// Object returned by the module
		
		
	
	/************************************************************************
 	*                    PRIVATE FUNCTION DECLARATIONS
 	*************************************************************************/
 	var onScroll;
 	
 	onScroll = function() {
 		$('.fixed-top').each(function(){
	 		var scroll_position, should_be_fixed,
	 			offset, top, is_fixed, start_offset,
	 			placeholder;
	 		
	 		// Get current scroll position
	 		scroll_position = $(window).scrollTop();
	 		
	 		// Get data embedded in element
	 		top = Number($(this).attr('data-top'));
	 		is_fixed = $(this).attr('data-is-fixed');
	 		offset = Number($(this).attr('data-offset'));
	 		start_offset = Number($(this).attr('data-start-offset'));
	 		placeholder = $(this).attr('data-placeholder');
	 		
	 		// Determine if the nav should be fixed
	 		should_be_fixed = ((scroll_position + offset + start_offset) > top);
	 		
	 		if (should_be_fixed && is_fixed === 'false') {
	 			$(this).css({'position': 'fixed',
	 									 'top': offset,
	 									 'width': $(this).width()});
	 		    $(this).attr('data-is-fixed', 'true');
	 		    
	 		    if (placeholder === 'true') {
		 		    $(this).after('<div class="scroll-placeholder" style="width: '
			 		    										+ $(this).width() 
			 		    										+ 'px; height: '
			 		    										+ $(this).height() 
			 		    										+ 'px"></div>');
		 		}
	 		    
	 		}
	 		else if (!should_be_fixed && is_fixed === 'true') {
	 			var next_element;
	 			
	 			$(this).css({'position': 'static',
	 						 'top': 'auto'});
	 			$(this).attr('data-is-fixed', 'false');
	 			
	 			next_element = $(this).next();
	 			if (placeholder === 'true' && $(next_element).hasClass('scroll-placeholder')) {
	 				$(next_element).remove();
	 			}
	 		}
 		});
 	};
	
	/************************************************************************
 	*                            TOP LEVEL CODE
 	*************************************************************************/
	/*
	 * Library object that contains public facing functions of the package.
	 */
	public_interface = {};
	
	
	// Initialization: jQuery function that gets called when 
	// the DOM tree finishes loading
	$(function() {
		// Inject fixed-top class into masthead
		$('.masthead').each(function(){
			$(this).addClass('fixed-top');
			$(this).attr('data-placeholder', 'true');
			$(this).css('z-index', '1000');
		});
		
		// Hide debug
		$('.masthead .debug').each(function(){
			$(this).remove();
		});
		
		// Fixed top elements
		$('.fixed-top').each(function() {
			var original_top, offset;
			original_top = $(this).offset().top;
				
			if (!$(this).attr('data-offset')) {
				$(this).attr('data-offset', '0');
			}
			
			if (!$(this).attr('data-start-offset')) {
				$(this).attr('data-start-offset', '0');
			}
			
			$(this).attr('data-top', original_top);
			$(this).attr('data-is-fixed', 'false');
		});
		
		// Bind onScroll to window scroll event for parallax effect
		$(window).bind('scroll', onScroll);		
		
		// Enable smooth scrolling
		// Credits: http://css-tricks.com/snippets/jquery/smooth-scrolling/
		// $('a[href*=#]:not([href=#])').click(function() {
			// if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
				// var target = $(this.hash);
				// target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
// 				
				// if (target.length) {
					// $('html,body').animate({
				    	// scrollTop: target.offset().top - 100 // Account for header here
				    // }, 1000);
// 				    
				    // return false;
				// }
			// }
		// });
	});

	return public_interface;

}()); // End of package wrapper

/*****************************************************************************
 *                      Public Functions
 *****************************************************************************/

function swap(element, kml_service) {
	console.log($(this).attr('onclick'));
	swapKmlService(kml_service);
}
 