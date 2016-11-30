/*****************************************************************************
 * FILE:    range_slider.js
 * DATE:    November 2016
 * AUTHOR:  Alan D. Snow
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var TETHYS_RANGE_SLIDER = (function() {
	// Wrap the library in a package function
	"use strict"; // And enable strict mode for this library

	/************************************************************************
 	*                      MODULE LEVEL / GLOBAL VARIABLES
 	*************************************************************************/
 	var public_interface;				// Object returned by the module

     /************************************************************************
 	*                    PRIVATE FUNCTION DECLARATIONS
 	*************************************************************************/
 	// private methods
 	var initRangeSlider;

 	initRangeSlider = function(tag) {

 	};

	/************************************************************************
 	*                            TOP LEVEL CODE
 	*************************************************************************/
	/*
	 * Library object that contains public facing functions of the package.
	 */
	public_interface = {
        initRangeSlider: initRangeSlider,

        updateSliderDisplayValue: function(value_for, range_input) {
            $('span.slider-value[for="' + value_for +'"]').html(range_input['value']);	
        }
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
function updateSliderDisplayValue(value_for, range_input) {
	TETHYS_RANGE_SLIDER.updateSliderDisplayValue(value_for, range_input);
}
