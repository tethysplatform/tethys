/*****************************************************************************
 * FILE:    d3_plot_view.js
 * DATE:    15 July 2015
 * AUTHOR: Ezra J. Rice
 * COPYRIGHT: (c) 2015 Brigham Young University
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var TETHYS_D3_PLOT_VIEW = (function() {
	// Wrap the library in a package function
	"use strict"; // And enable strict mode for this library

	/************************************************************************
 	*                      MODULE LEVEL / GLOBAL VARIABLES
 	*************************************************************************/
 	var public_interface;				// Object returned by the module



	/************************************************************************
 	*                    PRIVATE FUNCTION DECLARATIONS
 	*************************************************************************/
 	// Date picker private methods
 	var functionReviver, initD3Plot, initD3PiePlot;

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

	initD3Plot = function(element, json) {
	    var chart_type;

	    chart_type = json.chart_type;

	    if (chart_type === 'line_plot') {
	        initD3LinePlot(element, json);

	    } else if (chart_type === 'pie_plot') {
	        initD3PiePlot(element, json);
	    }
	};


	initD3PiePlot = function(element, json) {
	    var title = $(element).attr('data-title');
	    var subtitle = $(element).attr('data-subtitle');
	    var series = $.parseJSON($(element).attr('data-series'));

//	    $(element).D3({
            series.forEach(function (d) {
              d.value = +d.value;
              d.enabled = true;
            });

            var margin = {top: 40, right: 20, bottom: 30, left: 40},
                width = 960 - margin.left - margin.right,
                height = 500 - margin.top - margin.bottom;
            var radius = Math.min(width, height) / 2;
            var legendRectSize = 18;
            var legendSpacing = 4;

            var color = d3.scale.category20();

            var svg = d3.select($(element[0]))
              .append('svg')
              .attr('width', width)
              .attr('height', height)
              .append('g')
              .attr('transform', 'translate(' + (width / 2) +
                ',' + (height / 2) + ')');

            //Create the chart title and subtitle
            svg.append("text")
              .attr("x", 0 - (width/2 - margin.left))
              .attr("y", 0 - (height/2 - margin.top/2))
              .attr("text-anchor", "left")
              .style("font-size", "16px")
              .text(title);
            svg.append("text")
              .attr("x", 0 - (width/2 - margin.left))
              .attr("y", 0 - (height/2 - margin.top))
              .attr("text-anchor", "left")
              .style("font-size", "14px")
              .text(subtitle);

            var arc = d3.svg.arc()
              .outerRadius(radius);

            var pie = d3.layout.pie()
              .value(function(d) { return d.value; })
              .sort(null);

              //Create the variable and set up changes necessary for the tooltip

            var tooltip = d3.select($(element[0]))
              .append('div')
              .attr('class', 'tooltip');

            tooltip.append('div')
              .attr('class', 'name');

            tooltip.append('div')
              .attr('class', 'value');

            tooltip.append('div')
              .attr('class', 'percent');

              //End tooltip variable manipulation

            var path = svg.selectAll('path')
              .data(pie(series))
              .enter()
              .append('path')
              .attr('d', arc)
              .attr('fill', function (d, i) {
                return color(d.data.name);
              })
              .each(function (d) { this._current = d; });

              /*
              This function is what makes the tooltip appear when the mouse
              hovers over the section.
              */

              path.on('mouseover', function (d) {
                var total = d3.sum(series.map(function (d) {
                  return (d.enabled) ? d.value : 0;
                }));
                var percent = Math.round(1000 * d.data.value / total) / 10;
                tooltip.select('.name').html(d.data.name);
                tooltip.select('.value').html('Value: ' + d.data.value);
                tooltip.select('.percent').html(percent + '%');
                tooltip.style('display', 'block');
              });

              //End tooltip call function

              //Create legend

              var legend = svg.selectAll('.legend')
              .data(color.domain())
              .enter()
              .append('g')
              .attr('class', 'legend')
              .attr('transform', function(d, i) {
                var height = legendRectSize + legendSpacing;
                var offset =  height * color.domain().length / 2;
                var horz = -width / 2 + margin.left;
                var vert = i * height - offset;
                return 'translate(' + horz + ',' + vert + ')';
              });

            legend.append('rect')
              .attr('width', legendRectSize)
              .attr('height', legendRectSize)
              .style('fill', color)
              .style('stroke', color)
              .on('click', function (name) {
                var rect = d3.select(this);
                var enabled = true;
                var totalEnabled = d3.sum(series.map(function (d) {
                  return (d.enabled) ? 1 : 0;
                }));

                if (rect.attr('class') === 'disabled') {
                  rect.attr('class', '');
                } else {
                  if (totalEnabled < 2) return;
                  rect.attr('class', 'disabled');
                  enabled = false;
                }

                pie.value(function (d) {
                  if (d.name === name) d.enabled = enabled;
                  return (d.enabled) ? d.value : 0;
                });

                path = path.data(pie(series));

                path.transition()
                  .duration(750)
                  .attrTween('d', function (d) {
                    var interpolate = d3.interpolate(this._current, d);
                    this._current = interpolate(0);
                    return function (t) {
                      return arc(interpolate(t));
                    };
                  });
              });

            legend.append('text')
              .attr('x', legendRectSize + legendSpacing)
              .attr('y', legendRectSize - legendSpacing)
              .text(function(d) { return d; });

              //End of creating legend
//	    })
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
		// Initialize any d3 plots
		$('.d3-plot').each(function() {
		    if ($(this).attr('data-json')) {
		        var json_string, json;

                // Get string from data-json attribute of element
                json_string = $(this).attr('data-json');

                // Parse the json_string with special reviver
                json = JSON.parse(json_string, functionReviver);

		        initD3Plot(this, json);
		    }
		});
	});

	return public_interface;

}()); // End of package wrapper

/*****************************************************************************
 *                      Public Functions
 *****************************************************************************/
