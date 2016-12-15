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
 	var m_public_interface,				// Object returned by the module
 	    m_map,
 	    m_map_selector;

	/************************************************************************
 	*                    PRIVATE FUNCTION DECLARATIONS
 	*************************************************************************/
 	var resize_map;


 	/************************************************************************
 	*                    PRIVATE FUNCTION IMPLEMENTATIONS
 	*************************************************************************/

 	resize_map = function() {
 	    var header_height = $('.tethys-app-header').height(),
 	        window_height = $(window).height();
 	    $('#app-content, #inner-app-content').css('max-height', window_height - header_height);
 		$('#map_wrapper').css({
            'height': $('#app-content').height(),
            'max-height': $('#app-content').height(),
            'width': '100%',
        });
        m_map.render();
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
	    // Initialize module variables
	    var m_map_selector = '#map_view';
	    var m_map = TETHYS_MAP_VIEW.getMap();

	    // Events
        $(window).resize(function() {
            resize_map();

        });

        // Initialize map
        resize_map();
	});

	return m_public_interface;

}()); // End of package wrapper