/*****************************************************************************
 * FILE:    tethys_snippets.js
 * DATE:    5 November 2013
 * AUTHOR: Nathan R. Swain
 * COPYRIGHT: (c) 2013 Brigham Young University
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var TETHYS_SNIPPETS = (function() {
	// Wrap the library in a package function
	"use strict"; // And enable strict mode for this library
	
	/************************************************************************
 	*                      MODULE LEVEL / GLOBAL VARIABLES
 	*************************************************************************/
 	var map,							// GoogleEarth map object
		public_interface;				// Object returned by the module
		
		
	
	/************************************************************************
 	*                    PRIVATE FUNCTION DECLARATIONS
 	*************************************************************************/
 	// Date picker private methods
 	var functionReviver, initHighChartsPlot, initLinePlot;
 	
 	functionReviver = function(k, v) {
 		if (typeof v === 'string' && v.indexOf('function') !== -1) {
 			var fn;
 			// Pull out the 'function()' portion of the string
 			v = v.replace('function ()', '');
 			v = v.replace('function()', '');
 			
 			// Create a function from the string passed in
 			fn = Function(v);
 			
 			// Return the handle to the function that was created
 			return fn;
 		} else {
 			return v;
 		}
 	};
 	
	initHighChartsPlot = function(element, plot_type) {
		if ($(element).attr('data-json')) {
			var json_string, json;
			
			// Get string from data-json attribute of element
			json_string = $(element).attr('data-json');
			
			// Parse the json_string with special reviver
			json = JSON.parse(json_string, functionReviver);
			$(element).highcharts(json);
		}
		else if (plot_type === 'line' || plot_type === 'spline') {
			initLinePlot(element, plot_type);
		}
	};
	
	initLinePlot = function(element, plot_type) {
		var title = $(element).attr('data-title');
		var subtitle = $(element).attr('data-subtitle');
		var series = $.parseJSON($(element).attr('data-series'));
		var xAxis = $.parseJSON($(element).attr('data-xAxis'));
		var yAxis = $.parseJSON($(element).attr('data-yAxis'));
		
		$(element).highcharts({
			chart: {
				type: plot_type,
			},
	        title: {
	            text: title,
	            x: -20 //center
	        },
	        subtitle: {
	            text: subtitle,
	            x: -20
	        },
	        xAxis: {
	        	title: {
	        		text: xAxis['title']
	        	},
	        	labels: {
	                formatter: function() {
	                    return this.value + xAxis['label'];
	                }
	            },
	        },
	        yAxis: {
	            title: {
					text: yAxis['title']
	            },
	            labels: {
	                formatter: function() {
	                    return this.value + yAxis['label'];
	                }
	            },
	        },
	        tooltip: {
	            valueSuffix: '°C'
	        },
	        legend: {
	            layout: 'vertical',
	            align: 'right',
	            verticalAlign: 'middle',
	            borderWidth: 0
	        },
	        series: series
	    });
	};
	
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
		
		updateSliderDisplayValue: function(value_for, range_input) {
			$('span.slider-value[for="' + value_for +'"]').html(range_input['value']);	
		}
		
	};
	
	
	// Initialization: jQuery function that gets called when 
	// the DOM tree finishes loading
	$(function() {
		
		// Initialize any switch elements
		$('.bootstrap-switch').each(function() {
			$(this).bootstrapSwitch();
		});
		
		// Initialize any plots
		$('.highcharts-plot').each(function() {
			var plot_type = $(this).attr('data-type');
			initHighChartsPlot(this, plot_type);
		});
	});

	return public_interface;

}()); // End of package wrapper

/*****************************************************************************
 *                      Public Functions
 *****************************************************************************/
function remoteSubmit(formID) {
	"use strict";
	
	// Pass through the library object
	TETHYS_SNIPPETS.remoteSubmit(formID);
}

function updateSliderDisplayValue(value_for, range_input) {
	TETHYS_SNIPPETS.updateSliderDisplayValue(value_for, range_input); 	
}
 