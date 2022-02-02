/*****************************************************************************
 * FILE:    plot_view.js
 * DATE:    15 July 2015
 * AUTHOR: Ezra J. Rice
 * COPYRIGHT: (c) 2015 Brigham Young University
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var TETHYS_PLOT_VIEW = (function() {
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
 	var initD3Plot, initD3LinePlot, initD3PiePlot, initD3ScatterPlot, initHighChartsPlot,
 	    initD3BarPlot, initD3TimeSeriesPlot, processFormatters;

	initD3Plot = function(element, json) {
	    var chart_type;

	    chart_type = json.chart_type;
        var svg;
	    if ('type' in json.chart) {
	        if (json.chart.type === 'line' || json.chart.type === 'spline') {
	            initD3LinePlot(element, json);
            } else if (json.chart.type === 'scatter') {
                initD3ScatterPlot(element, json);
            } else if (json.chart.type === 'column' || json.chart.type === 'bar') {
                initD3BarPlot(element, json);
            } else if (json.chart.type === 'area') {
                initD3TimeSeriesPlot(element, json);
            }
	    } else  if ('plotOptions' in json) {
	        var plot_options = json.plotOptions;
	        if ('pie' in plot_options) {
	            initD3PiePlot(element, json);
	        }
	    }
	};

    initD3LinePlot = function(element, json) {

        var title = json.title.text;
        var subtitle = json.subtitle.text;
        var x_axis_title = json.xAxis.title.text;
        var x_axis_formatter = json.xAxis.labels.formatter;
        var y_axis_title = json.yAxis.title.text;
        var y_axis_formatter = json.yAxis.labels.formatter;
        var series = json.series;

        var number_of_series = d3.max(Object.keys(series));
        var number_of_points = d3.max(Object.keys(series[0].data));

        var margin = {top: 40, right: 80, bottom: 30, left: 50};

        var svg = d3.select(element).append("svg")
            .attr("width", "100%")
            .attr("height", "100%");

        var width = svg.node().getBoundingClientRect().width - margin.left - margin.right;
        var height = svg.node().getBoundingClientRect().height - margin.top - margin.bottom;

        svg = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        var x = d3.scaleLinear()
            .range([0, width]);

        var y = d3.scaleLinear()
            .range([height, 0]);

        var color = d3.scaleOrdinal(d3.schemeCategory10);

        var xAxis = d3.axisBottom()
            .scale(x);

        var yAxis = d3.axisLeft()
            .scale(y);

        var dataCallback = function (d, i, j) {
            d[i].x.push(series[i].data[j][0]);
            d[i].y.push(series[i].data[j][1]);
        };

        for (var i = 0; i <= number_of_series; i++) {

            series[i].x = [];
            series[i].y = [];

            for (var j = 0; j <= number_of_points; j++) {
                dataCallback(series, i, j);
            }
        }

        if (json.chart.type === 'spline') {
            var line_type = d3.curveCardinal;
        } else {
            var line_type = d3.curveLinear;
        }

        var line = d3.line()
            .curve(line_type)
            .x(function (d) { return x(d[0]); })
            .y(function (d) { return y(d[1]); });

        var tip = d3.tip()
            .attr('class', 'd3-tip')
            .offset([-10, 0])
            .html(function (event, d) {
                return x_axis_title + ": <span style='color:yellow'>"
                    + d[0] + "</span> </br>" + y_axis_title + ": <span style='color:yellow'>" + d[1] + "</span>";
            });



        //Create the chart title and subtitle
        svg.append("text")
            .attr("x", (width/2))
            .attr("y", 0 - (margin.top / 2))
            .attr("text-anchor", "middle")
            .style("font-size", "16px")
            .text(title);
        svg.append("text")
            .attr("x", (width/2))
            .attr("y", 0 - (margin.top / 8))
            .attr("text-anchor", "middle")
            .style("font-size", "14px")
            .text(subtitle);

        svg.call(tip);

        x.domain([
            d3.min(series, function (d, i) { return d3.min(series[i].x); }) - 5,
            d3.max(series, function (d, i) { return d3.max(series[i].x); }) + 5
        ]);

        y.domain([
            d3.min(series, function (d, i) { return d3.min(series[i].y); }) - 5,
            d3.max(series, function (d, i) { return d3.max(series[i].y); }) + 5
        ]);

        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis)
            .append("text")
                .attr("x", width)
                .attr("y", -6)
                .attr("dx", ".71em")
                .style("text-anchor", "end")
                .text(x_axis_title);

        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
            .append("text")
                .attr("transform", "rotate(-90)")
                .attr("y", 6)
                .attr("dy", ".71em")
                .style("text-anchor", "end")
                .text(y_axis_title);

        var lineNames = svg.selectAll(".line")
            .data(series)
            .enter().append("g")
                .attr("class", "line");

        lineNames.append("path")
            .attr("class", "line")
            .attr("d", function (d) { return line(d.data); })
            .attr("stroke-width", 2)
            .style("stroke", function (d) { return color(d.name); });

        for (var i = 0; i <= number_of_series; i++) {
            svg.selectAll("point")
                .data(series[i].data)
                .enter().append("path")
                    .attr("class", "point")
                    .attr("d", d3.symbol().type(d3.symbolCircle))
                    .attr("transform", function (d) { return "translate(" + x(d[0]) + "," + y(d[1]) + ")"; })
                    .style("fill", function (d) {return color(series[i].name); })
                    .on("mouseover", tip.show)
                    .on("mouseout", tip.hide);
        };

        // draw legend
        var legend = svg.selectAll(".legend")
            .data(color.domain())
            .enter().append("g")
                .attr("class", "legend")
                .attr("transform", function (d, i) { return "translate(0," + i * 20 + ")"; });

        // draw legend colored rectangles
        legend.append("rect")
            .attr("x", width - 18)
            .attr("y", 8)
            .attr("width", 18)
            .attr("height", 3)
            .style("fill", color);

        // draw legend text
        legend.append("text")
            .attr("x", width)
            .attr("y", 9)
            .attr("dy", ".35em")
            .style("text-anchor", "beginning")
            .text(function (d) { return d; });
    };

	initD3PiePlot = function(element, json) {
	    var title = json.title.text;
	    var subtitle = json.subtitle.text;
	    var series = json.series;

            series.forEach(function (d) {
              d.value = +d.value;
              d.enabled = true;
            });

            var svg = d3.select(element).append('svg')
              .attr('width', "100%")
              .attr('height', "100%")

            var margin = {top: 40, right: 80, bottom: 30, left: 50};

            var width = svg.node().getBoundingClientRect().width - margin.left - margin.right;
            var height = svg.node().getBoundingClientRect().height - margin.top - margin.bottom;

            var radius = Math.min(width, height) / 2;
            var legendRectSize = 18;
            var legendSpacing = 4;

            var color = d3.scaleOrdinal(d3.schemeCategory10);//d3.scaleOrdinal(d3.schemeSpectral);

            svg.append("g")
              .attr('transform', 'translate(0,' + height + ')');

            //Create the chart title and subtitle
            svg.append("text")
              .attr("x", width/2)
              .attr("y", margin.top/3)
              .attr("text-anchor", "middle")
              .style("font-size", "16px")
              .text(title);
            svg.append("text")
              .attr("x", width/2)
              .attr("y", margin.top*2/3)
              .attr("text-anchor", "middle")
              .style("font-size", "14px")
              .text(subtitle);

            var arc = d3.arc()
              .outerRadius(radius)
              .innerRadius(0);

            var pie = d3.pie()
              .value(function(d) { return d.value; })
              .sort(null);

            //Create the variable and set up changes necessary for the tooltip

            var tooltip = d3.tip()
                .attr('class', 'd3-tip')
                .html(function (event, d) {
                var total = d3.sum(series.map(function (d) {
                  return (d.enabled) ? d.value : 0;
                }));
                var percent = Math.round(1000 * d.data.value / total) / 10;
                    return "<strong>" + d.data.name + "</strong><br>" + 'Value: ' + d.data.value + "<br>" + percent + '%';
                });

            svg.call(tooltip);

            //End tooltip variable manipulation
            var path = svg.selectAll('path')
              .data(pie(series))
              .enter()
              .append('path')
              .attr('d', arc)
              .attr('fill', function (d, i) {
                return color(d.data.name);
              })
              .attr("transform", "translate(" + width/2 + "," + (height/2 + margin.top) + ")")
              .each(function (event, d) { this._current = d; })
              .on('mouseover', tooltip.show)
              .on('mousemove', function(event, d){ return tooltip.style("top",
                  (event.screenX-75) + "px").style("left", (event.screenY-50) + "px");})
              .on('mouseout', tooltip.hide);

              //Create legend
              var legend = svg.selectAll('.legend')
              .data(color.domain())
              .enter()
              .append('g')
              .attr('class', 'legend')
              .attr('transform', function(d, i) {
                var height2 = legendRectSize + legendSpacing;
                var offset =  height2 * color.domain().length / 2;
                var horz = width;
                var vert = i * height2 + offset;
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
	};

	initD3ScatterPlot = function(element, json) {
	    var title = json.title.text;
	    var subtitle = json.subtitle.text;
	    var x_axis_title = json.xAxis.title.text;
        var y_axis_title = json.yAxis.title.text;
        var series = json.series;

        var color = d3.scaleOrdinal().range(d3.schemeSet1);

        var svg = d3.select(element).append("svg")
            .attr("width", "100%")
		    .attr("height", "100%");

        var margin = {top: 40, right: 80, bottom: 30, left: 50};

        var width = svg.node().getBoundingClientRect().width - margin.left - margin.right;
        var height = svg.node().getBoundingClientRect().height - margin.top - margin.bottom;

        svg = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        var x = d3.scaleLinear()
            .range([0, width]);

        var y = d3.scaleLinear()
            .range([height, 0]);

        var xAxis = d3.axisBottom()
            .scale(x);

        var yAxis = d3.axisLeft()
            .scale(y);

        var tip = d3.tip()
            .attr('class', 'd3-tip')
            .offset([-10, 0])
            .html(function (event, d) {
                return x_axis_title + ": <span style='color:yellow'>"
                    + d[0] + "</span> </br>" + y_axis_title + ": <span style='color:yellow'>" + d[1] + "</span>";
            });

        svg.call(tip);

        //Create the chart title and subtitle
        svg.append("text")
            .attr("x", (width/2))
            .attr("y", 0 - (margin.top / 2))
            .attr("text-anchor", "middle")
            .style("font-size", "16px")
            .text(title);
        svg.append("text")
            .attr("x", (width/2))
            .attr("y", 0 - (margin.top / 8))
            .attr("text-anchor", "middle")
            .style("font-size", "14px")
            .text(subtitle);

        var number_of_series = series.length;

        var dataPoints = function (d, i, j) {
            d[i].x.push(series[i].data[j][0]);
            d[i].y.push(series[i].data[j][1]);
        };

        for (var i = 0; i < number_of_series; i++) {
            var number_of_points = series[i].data.length;
            series[i].x = [];
            series[i].y = [];

            for (var j = 0; j < number_of_points; j++) {
                dataPoints(series, i, j);
            };
        };

        // don't want dots overlapping axis, so add in buffer to data domain
        x.domain([
            d3.min(series, function (d, i) { return d3.min(series[i].x); }) - 5,
            d3.max(series, function (d, i) { return d3.max(series[i].x); }) + 5
        ]);

        y.domain([
            d3.min(series, function (d, j) { return d3.min(series[j].y); }) - 5,
            d3.max(series, function (d, j) { return d3.max(series[j].y); }) + 5
        ]);

        // x-axis
        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis)
            .append("text")
                .attr("class", "label")
                .attr("x", width)
                .attr("y", -6)
                .style("text-anchor", "end")
                .text(x_axis_title);

        // y-axis
        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
            .append("text")
                .attr("class", "label")
                .attr("transform", "rotate(-90)")
                .attr("y", 6)
                .attr("dy", ".71em")
                .style("text-anchor", "end")
                .text(y_axis_title);

        for (var i = 0; i < number_of_series; i++) {

            var seriesData = series[i].data;

            // draw dots
            svg.selectAll("point")
                .data(seriesData)
                .enter().append("path")
                    .attr("class", "point")
                    .attr("d", d3.symbol().type(d3.symbolCircle))
                    .attr("transform", function (d) { return "translate(" + x(d[0]) + "," + y(d[1]) + ")"; })
                    .style("fill", function (d) { return color(series[i].name); })
                    .on("mouseover", tip.show)
                    .on("mouseout", tip.hide);
        }

            // draw legend
            var legend = svg.selectAll(".legend")
                .data(color.domain())
                .enter().append("g")
                    .attr("class", "legend")
                    .attr("transform", function (d, i) { return "translate(0," + i * 20 + ")"; });

            // draw legend colored rectangles
            legend.append("rect")
                .attr("x", width)
                .attr("width", 18)
                .attr("height", 18)
                .style("fill", color);

            // draw legend text
            legend.append("text")
                .attr("x", width + 20)
                .attr("y", 9)
                .attr("dy", ".35em")
                .style("text-anchor", "start")
                .text(function (d) { return d; });
	};

	initD3BarPlot = function(element, json) {
	    var title = json.title.text;
	    var subtitle = json.subtitle.text;
	    var axisTitle = json.yAxis.title.text;
	    var categories = json.xAxis.categories;
	    var series = json.series;

	    var svg = d3.select(element).append("svg")
		            .attr("width", "100%")
		            .attr("height", "100%");

	    var margin = {top: 40, right: 80, bottom: 30, left: 50};

        var width = svg.node().getBoundingClientRect().width - margin.left - margin.right;
        var height = svg.node().getBoundingClientRect().height - margin.top - margin.bottom;

        svg = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        var x0 = d3.scaleBand()
            .rangeRound([0, width], .1);

        var x1 = d3.scaleBand();

        var y = d3.scaleLinear()
            .range([height, 0]);

        var color = d3.scaleOrdinal(d3.schemeCategory10);//d3.scaleOrdinal(d3.schemeSpectral);

        var xAxis = d3.axisBottom()
            .scale(x0);

        var yAxis = d3.axisLeft()
            .scale(y)
            .tickFormat(d3.format(".2s"));

        var tip = d3.tip()
            .attr('class', 'd3-tip')
            .offset([-10, 0])
            .html(function (event, d) {
                var category_index = categories.indexOf(event.path[1].__data__);
                return "<strong>" + d.name + ":</strong> <span style='color:yellow'>" + d.data[category_index] + "</span>";
            });

        //Create the chart title and subtitle
        svg.append("text")
            .attr("x", (width/2))
            .attr("y", 0 - (margin.top / 2))
            .attr("text-anchor", "middle")
            .style("font-size", "16px")
            .text(title);
        svg.append("text")
            .attr("x", (width/2))
            .attr("y", 0 - (margin.top / 8))
            .attr("text-anchor", "middle")
            .style("font-size", "14px")
            .text(subtitle);

        svg.call(tip);

        x0.domain(categories);
        x1.domain(Object.keys(series)).rangeRound([0, x0.bandwidth()]);
        y.domain([0, d3.max(series, function (d) { return d3.max(d.data); })]);

        svg.append("g")
              .attr("class", "x axis")
              .attr("transform", "translate(0," + height + ")")
              .call(xAxis);

        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
            .append("text")
                .attr("transform", "rotate(-90)")
                .attr("y", 6)
                .attr("dy", ".71em")
                .style("text-anchor", "end")
                .text(axisTitle);

        var period = svg.selectAll(".period")
            .data(categories)
            .enter().append("g")
                .attr("class", "g")
                .attr("transform", function (d, i) { return "translate(" + x0(d) + ",0)"; });

        period.selectAll("rect")
            .data(series)
            .enter().append("rect")
                .attr("width", x1.bandwidth())
                .attr("x", function (d) { return x0(d); })
                .attr("y", function (d, i, j) {
                  var category_index = categories.indexOf(j[i].parentElement.__data__);
                  return y(d.data[category_index]);
                })
                .attr("height", function (d, i, j) {
                  var category_index = categories.indexOf(j[i].parentElement.__data__);
                  return height - y(d.data[category_index]);
                })
                .attr("transform", function (d, i) {
                var val = x1.range()[1]/series.length * i + 1;
                return "translate(" + val +",0)";
                })
                .style("fill", function (d) { return color(d.name); })
                .on('mouseover', tip.show)
                .on('mouseout', tip.hide);

        var legend = svg.selectAll(".legend")
            .data(series.slice().reverse())
            .enter().append("g")
                .attr("class", "legend")
                .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

        legend.append("rect")
            .attr("x", width)
            .attr("width", 18)
            .attr("height", 18)
            .style("fill", function (d) { return color(d.name); });

        legend.append("text")
            .attr("x", width + 20)
            .attr("y", 9)
            .attr("dy", ".35em")
            .style("text-anchor", "start")
            .text(function (d) { return d.name; });
	};

	initD3TimeSeriesPlot = function(element, json) {
	    var title = json.title.text;
	    var y_axis_title = json.yAxis.title.text;;
	    var series = json.series;

	    var color = d3.scaleOrdinal(d3.schemeCategory10);//d3.scaleOrdinal(d3.schemeSpectral);

	    var number_of_series = series.length;

	    var svg = d3.select(element).append("svg")
		            .attr("width", "100%")
		            .attr("height", "100%");

	    var margin = {top: 40, right: 100, bottom: 30, left: 50};

        var width = svg.node().getBoundingClientRect().width - margin.left - margin.right;
        var height = svg.node().getBoundingClientRect().height - margin.top - margin.bottom;

        svg = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        function timeConverter(UNIX_timestamp){
            var MS_MINUTES = 60000;
            var a = new Date(UNIX_timestamp);
            var tz_offset = a.getTimezoneOffset();
            var z = new Date(UNIX_timestamp + tz_offset * MS_MINUTES);
            var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
            var year = z.getFullYear();
            var month = months[z.getMonth()];
            var date = z.getDate();
            var hour = z.getHours();
            var min = z.getMinutes();
            var sec = z.getSeconds();
            var time = date + ' ' + month + ' ' + year + ' ' + hour + ':' + min + ':' + sec ;
            return time;
        }

        var x = d3.scaleTime()
            .range([0, width]);

        var y = d3.scaleLinear()
            .range([height, 0]);

        var xAxis = d3.axisBottom()
            .scale(x)
            .tickFormat(d3.timeFormat("%d %b '%y %I:%M:%S"));

        var yAxis = d3.axisLeft()
            .scale(y);

        var dataCallback = function (d, i, j) {
            d[i].x.push(series[i].data[j][0]);
            d[i].y.push(series[i].data[j][1]);
        };

        for (var i = 0; i < number_of_series; i++) {
            var number_of_points = series[i].data.length;
            series[i].x = [];
            series[i].y = [];

            for (var j = 0; j < number_of_points; j++) {
                dataCallback(series, i, j);
            }
        }

        var area = d3.area()
            .x(function(d) { return x(d[0]); })
            .y0(height)
            .y1(function(d) { return y(d[1]); });

        var line = d3.line()
            .x(function (d) { return x(d[0]); })
            .y(function (d) { return y(d[1]); })
            .curve(d3.curveLinear);

        var tip = d3.tip()
            .attr('class', 'd3-tip')
            .offset([-10, 0])
            .html(function (event, d) {
                return "Date: <span style='color:yellow'>"
                    + timeConverter(d[0]) + "</span> </br>"
                    + y_axis_title + ": <span style='color:yellow'>" + d[1] + "</span>";
            });

        svg.call(tip);

        //Create the chart title and subtitle
        svg.append("text")
            .attr("x", (width/2))
            .attr("y", 0 - (margin.top / 2))
            .attr("text-anchor", "middle")
            .style("font-size", "16px")
            .text(title);

        x.domain([
            d3.min(series, function (d, i) { return d3.min(d.x); }),
            d3.max(series, function (d, i) { return d3.max(d.x); })
        ]);

        y.domain([
            d3.min(series, function (d, j) { return d3.min(series[j].y); }),
            d3.max(series, function (d, j) { return d3.max(series[j].y); })
        ]);


        var lineNames = svg.selectAll(".line")
        .data(series)
        .enter().append("g")
            .attr("class", "line");

        lineNames.append("path")
            .attr("class", "line")
            .attr("d", function (d) { return line(d.data); })
            .attr("stroke-width", 2)
            .style("stroke", function (d) { return color(d.name); });

        for (var i = 0; i < number_of_series; i++) {
            var seriesData = series[i].data;

            svg.append("path")
                .datum(seriesData)
                .attr("class", "area")
                .attr("d", area)
                .style("fill", function (d) { return color(series[i].name); })
                .style("opacity", 0.5);
        };
        for (var i = 0; i < number_of_series; i++) {
            var seriesData = series[i].data;

            svg.selectAll("point")
                .data(seriesData)
                .enter().append("path")
                    .attr("class", "point")
                    .attr("d", d3.symbol().type(d3.symbolCircle))
                    .attr("transform", function (d) { return "translate(" + x(d[0]) + "," + y(d[1]) + ")"; })
                    .style("fill", function (d) {return color(series[i].name); })
                    .on("mouseover", tip.show)
                    .on("mouseout", tip.hide);
        };

        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis);

        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
            .append("text")
                .attr("transform", "rotate(-90)")
                .attr("y", 6)
                .attr("dy", ".71em")
                .style("text-anchor", "end")
                .text(y_axis_title);

        var legend = svg.selectAll(".legend")
            .data(series.slice().reverse())
            .enter().append("g")
                .attr("class", "legend")
                .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

        legend.append("rect")
            .attr("x", width + margin.right -18)
            .attr("width", 18)
            .attr("height", 18)
            .style("fill", function (d) { return color(d.name); });

        legend.append("text")
            .attr("x", width + margin.right - 20)
            .attr("y", 9)
            .attr("dy", ".35em")
            .style("text-anchor", "end")
            .text(function (d) { return d.name; });
	};

	initHighChartsPlot = function(element) {
        var plot_type = $(element).attr('data-type');
        if ($(element).attr('data-json')) {
            var json_string, json;

            // Get string from data-json attribute of element
            json_string = $(element).attr('data-json');

            // Parse the json_string with special reviver
            json = JSON.parse(json_string);

            // Handle fornatter functions
            json = processFormatters(json);

            $(element).highcharts(json);
        }
        else if (plot_type === 'line' || plot_type === 'spline') {
            initLinePlot(element, plot_type);
        }
    };

    processFormatters = function(json) {
        if ('xAxis' in json && 'labels' in json.xAxis && 'units' in json.xAxis.labels) {
            const {units, ...labels} = json.xAxis.labels;
            labels.formatter = function() {
                return this.value + " " + units;
            };
            json.xAxis.labels = labels;
        }

        if ('yAxis' in json && 'labels' in json.yAxis && 'units' in json.yAxis.labels) {
            const {units, ...labels} = json.yAxis.labels;
            labels.formatter = function() {
                return this.value + " " + units;
            };
            json.yAxis.labels = labels;
        }

        if ('tooltip' in json && 'phrase_one' in json.tooltip && 'phrase_two' in json.tooltip) {
            const {phrase_one, phrase_two, ...tooltip} = json.tooltip;
            tooltip.formatter = function() {
                return "<b>" 
                    + this.series.xAxis.categories[this.point.x] 
                    + "</b> " + phrase_one + " <br><b>" + this.point.value 
                    + "</b> " + phrase_two + " <br><b>" + this.series.yAxis.categories[this.point.y] 
                    + "</b>";
            };
            json.tooltip = tooltip;
        }
        return json;
    };

	/************************************************************************
 	*                            TOP LEVEL CODE
 	*************************************************************************/
	/*
	 * Library object that contains public facing functions of the package.
	 */
	public_interface = {
        initHighChartsPlot: initHighChartsPlot,
     };


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
                json = JSON.parse(json_string);

                // Handle fornatter functions
                json = processFormatters(json);

		        initD3Plot(this, json);
		    }
		});

		// Initialize any plots
		$('.highcharts-plot').each(function() {
			initHighChartsPlot(this);
		});
	});

	var redraw = true;

	$(window).resize(function() {

	    // Initialize any d3 plots
	    if(redraw) {
	        redraw = false;
	        $('.d3-plot').each(function() {
                $(this).empty();
                if ($(this).attr('data-json')) {
                    var json_string, json;

                    // Get string from data-json attribute of element
                    json_string = $(this).attr('data-json');

                    // Parse the json_string with special reviver
                    json = JSON.parse(json_string);

                    // Handle fornatter functions
                    json = processFormatters(json);

                    initD3Plot(this, json);
		        }
		    });
		    redraw = true;
	    }

	});

	return public_interface;

}()); // End of package wrapper
