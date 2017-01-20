/*****************************************************************************
 * FILE:      tethys_gizmos.js
 * DATE:      5 November 2013
 * AUTHOR:    Nathan R. Swain
 * COPYRIGHT: (c) Brigham Young University 2013
 * LICENSE:   BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var TETHYS_GIZMOS = (function() {
	// Wrap the library in a package function
	"use strict"; // And enable strict mode for this library
	
	/************************************************************************
 	*                      MODULE LEVEL / GLOBAL VARIABLES
 	*************************************************************************/
 	var public_interface;				// Object returned by the module
		
	/************************************************************************
 	*                    PRIVATE FUNCTION DECLARATIONS
 	*************************************************************************/
	
	/************************************************************************
 	*                            TOP LEVEL CODE
 	*************************************************************************/
	/*
	 * Library object that contains public facing functions of the package.
	 */
	public_interface = {
		
		// Click Submit from Remote Button
		remoteSubmit:  function(formID) {
			// Code here
			$(formID).submit();
		},
	};
	
	// Initialization: jQuery function that gets called when 
	// the DOM tree finishes loading
	$(function() {

	});

	return public_interface;

}()); // End of package wrapper

/*****************************************************************************
 *                      Public Functions
 *****************************************************************************/
function remoteSubmit(formID) {
	"use strict";
	
	// Pass through the library object
	TETHYS_GIZMOS.remoteSubmit(formID);
}
