/*****************************************************************************
 * FILE:    JavaScript Enclosure Template
 * DATE:    D MMMMMMM YYYY
 * AUTHOR:
 * COPYRIGHT: (c) Brigham Young University XXXX
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var TETHYS_MAP_VIEW_LAYOUT = (function() {
	// Wrap the library in a package function
	"use strict"; // And enable strict mode for this library

	/************************************************************************
 	*                      MODULE LEVEL / GLOBAL VARIABLES
 	*************************************************************************/
 	var m_public_interface;				// Object returned by the module

	/************************************************************************
 	*                    PRIVATE FUNCTION DECLARATIONS
 	*************************************************************************/
 	var handle_save, resize_map;


 	/************************************************************************
 	*                    PRIVATE FUNCTION IMPLEMENTATIONS
 	*************************************************************************/
    handle_save = function() {
        console.log('foo');
        // Get the JSON from the hidden field
        // Build AJAX
        // map?type="on-save"&var1="foo"&var2="bar"
    };

 	resize_map = function() {
 	    var header_height = $('.tethys-app-header').height(),
 	        window_height = $(window).height();
 	    $('#app-content, #inner-app-content').css('max-height', window_height - header_height);
 		$('#map_wrapper').css({
            'height': $('#app-content').height(),
            'max-height': $('#app-content').height(),
            'width': '100%',
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
	m_public_interface = {};

	/************************************************************************
 	*                  INITIALIZATION / CONSTRUCTOR
 	*************************************************************************/
	$(function() {

	    // Bind to events
        $(window).resize(function() {
            resize_map();
        });

        // Save event
        $('#save-btn').click(handle_save);

        // Initialize map
        resize_map();
	});

	return m_public_interface;

}()); // End of package wrapper