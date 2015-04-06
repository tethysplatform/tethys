/*****************************************************************************
 * FILE:    fetchclimate_plot.js
 * DATE:    7/25/2014
 * AUTHOR: Alan Snow
 * COPYRIGHT: (c) 2014 Brigham Young University
 * LICENSE: BSD 2-Clause
 *****************************************************************************/
if(jQuery('#fetchclimate_plot').length > 0) {
  /*****************************************************************************
   *                      CUSTOM FUNCTIONS
   *****************************************************************************/
  String.prototype.toProperCase = function () {
    return this.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
  };

  /*****************************************************************************
   *                      LIBRARY WRAPPER
   *****************************************************************************/

  var FETCHCLIMATE_PLOT = (function() {
    // Wrap the library in a package function
    "use strict"; // And enable strict mode for this library
    
    /************************************************************************
     *                      MODULE LEVEL / GLOBAL VARIABLES
     *************************************************************************/
     var m_public_interface, // Object returned by the module
        m_date_queries, m_date_query_sizes, m_date_query_size, m_all_data,
        m_request_complete, m_all_ajax_requests; 
    
    /************************************************************************
     *                    PRIVATE FUNCTION DECLARATIONS
     *************************************************************************/
     var updateStatus, checkStatus, getNumPoints, getPercentage, giveStatusUpdate,
      getPlotData, initHighCharts, abortAllAjaxRequests, removeHighCharts, 
      addLoadingAttrToCharts;


     /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/
    //updates the status of the request for the user
    updateStatus = function(bar, grid_name, variable_name, status, percentage) {
      console.log(grid_name + ' ('+variable_name+'): Receiving:'+percentage+'%'+'...');
      if (status !== 'error') {
        // Update progress bar percentage
        bar.css('width', percentage + '%');
        bar.attr('aria-valuenow',percentage)
        bar.text(status.toProperCase()+"...");
      } else {
        // Set status to error
        bar.text('ERROR!');
        bar.addClass('progress-bar-danger');
      }
    };

    //checks calculation status of request
    checkStatus = function(bar, stat_var, stat_hash, stat_response) {
      request = jQuery.ajax({
        type: "POST",
        url: "/apps/snippets-ajax/fetchclimate/statusCheck",
        data: { variable : stat_var, 
          hash : stat_hash,
          responseUri : stat_response}
      }).done(function(data) {
        updateStatus(bar, data.status, data.statusData);
        if(data.status !== 'receiving') {
          //Set timeout to check again
          setTimeout(function() { checkStatus(bar, stat_var, stat_hash, stat_response); }, 3000);
        }
      });
    };

    //gives the percent complete
    getPercentage = function(series_indexes_received) {
      var tot_size_received = 0;
      series_indexes_received.map(function(index) {
        tot_size_received += m_date_query_sizes[index];
      });
      return 100*tot_size_received/m_date_query_size;
    };

    //gives the user the status update
    giveStatusUpdate = function(chart_HTML, grid_name, variable_name, series_index,series_indexes_received) {
        var percentage = Math.round(getPercentage(series_indexes_received));
        updateStatus(chart_HTML.find('.progress-bar'), grid_name, variable_name, 
          'Receiving:'+percentage+'%',percentage);
    };

    //gets data for each plot
    getPlotData = function() {
      var serverURL = jQuery('#fc_outer_container').attr('data-server-url');
      var   m_all_ajax_requests = [];
      var ajax_url = jQuery('#fc_outer_container').attr('data-ajax-url');
      //loop through all of the charts added
      var charts = jQuery("#fetchclimate_plot .highcharts-plot").each(function() {
        var chart_HTML = jQuery(this);
        var chart = chart_HTML.highcharts();
        var grid = JSON.parse(chart_HTML.attr('geometry'));
        var variable = JSON.parse(chart_HTML.attr('variable'));
        var series_indexes_received = [];
        var chart_data = [];
        //Perform ajax request for each of the date queries
        var requests = m_date_queries.map(function(dateQuery, series_index) {
          return jQuery.ajax({
              type: "GET",
              url: ajax_url,
              dataType: "json",
              data: { 
                      serviceUrl: (serverURL.length>0?serverURL:''),
                      variable : JSON.stringify(variable), 
                      grid : JSON.stringify(grid),
                      time : JSON.stringify(dateQuery)
                    },
              success: function(data) {
                series_indexes_received.push(series_index);
                console.log(grid.gridData.title + ' ('+variable.name+'): '+series_indexes_received.length+'/'+m_date_queries.length);
                giveStatusUpdate(chart_HTML,grid.gridData.title,variable.name,series_index,series_indexes_received);
            }
          });
        });
        m_all_ajax_requests = m_all_ajax_requests.concat(requests);
        //When all of the requests are completed
        jQuery.when.apply(jQuery, requests).then(function() {
          var data = [];
          var all_data = [];
          //if there are more than one queries
          if (arguments[0].length == 3) {
          //get all of the return data
            var all_data = [].map.call(arguments, function(arg) {
              return arg[0];
            });
            console.log(arguments.length);
            //combine the data and check if there is data
            all_data.map(function(part_data) {
              if(typeof part_data !== 'undefined') {
                data = data.concat(part_data.data);
              }
            });
          } 
          //if there is only one query
          else {
            if(arguments[0] != false && typeof arguments != 'undefined' && typeof arguments[0] != 'undefined') {
              data = arguments[0].data;
              all_data = [arguments[0]];
            }
          }
          //if there is data
          if (data.length>0 && typeof all_data[0] !== 'undefined') {
            m_all_data[variable.name][grid.gridData.title] = data;
            var new_name = all_data[0].dataName + " (" + all_data[0].dataUnits + ")";
            chart.series[0].setData(data);
            chart.yAxis[0].setTitle({text: new_name});
            chart.series[0].update({name:new_name});
            chart_HTML.removeClass('plot-parent');
            chart_HTML.find('.highcharts-container').removeClass('plot-overlay');
            chart_HTML.find('.progress').remove();
          } else {
            m_all_data[variable.name][grid.gridData.title] = null;
            chart_HTML.find('.progress-bar').text('ERROR LOADING!');
            chart_HTML.find('.progress-bar').addClass('progress-bar-danger');
          }
          var one_request_complete_event = new CustomEvent('fcOneDataRequestComplete', {'detail': {variable: variable, grid: grid, data: data}});
          jQuery('#fetchclimate_plot')[0].dispatchEvent(one_request_complete_event);
        });
      });

      jQuery.when.apply(jQuery, m_all_ajax_requests).then(function() {
        console.log("Your request is complete. You can view the data in the console and you can access" +
          "the data through the Javascript API in the snippets documentation."); 
        m_request_complete = true;
        var request_complete_event = new CustomEvent('fcDataRequestComplete', {'detail': m_all_data});
        jQuery('#fetchclimate_plot')[0].dispatchEvent(request_complete_event);
      });
    };

    //intializes the highcharts before loading data
    initHighCharts = function() {
      //abort any remaining past requests
      abortAllAjaxRequests();
      m_request_complete = false;
      m_all_data = {};
      if(typeof FETCHCLIMATE_MAP !== 'undefined') {
        var grids_json = FETCHCLIMATE_MAP.getGridsJSON();
        var points_json = FETCHCLIMATE_MAP.getPointsJSON();
      }
      else {
        var grids_json = JSON.parse(jQuery('#fc_outer_container').attr('data-grids'));
        var points_json = JSON.parse(jQuery('#fc_outer_container').attr('data-points'));
      }

      var variables_json = JSON.parse(jQuery('#fc_outer_container').attr('data-variables'));
      var high_chart = {
                          chart: {
                            type: 'area',
                            zoomType: 'x',
                            shadow: true,
                            spacing: [15,30,20,15]
                          },
                          title: {
                            text: 'Time Series Loading'
                          },
                          xAxis: {
                            type: 'datetime',
                            maxZoom: 24 * 3600 * 1000
                          },
                          yAxis: {
                            title: {text: ''}
                          },
                          legend: {
                            enabled: false
                          },
                          series: [{
                            name: 'Variable',
                            data: []
                          }]
                        };
      //set plot dimensions
      if(typeof jQuery("#fetchclimate_plot").attr('data-plot-dimensions')!='undefined') {
        var plot_dimensions = JSON.parse(jQuery("#fetchclimate_plot").attr('data-plot-dimensions'));
        console.log(plot_dimensions);
        if(typeof plot_dimensions.width != 'undefined') {
          high_chart.chart.width = plot_dimensions.width;
        }
        if(typeof plot_dimensions.height != 'undefined') {
          high_chart.chart.height = plot_dimensions.height;
        } else {
          high_chart.chart.height = 500;
        }
      }
      var plot_html = '<div class="highcharts-plot"></div>';
      for (var variable in variables_json) {
        m_all_data[variable] = {};
        high_chart.yAxis.title.text = variable;
        high_chart.series.name = variable;
        for (var grid_id in grids_json) {
          high_chart.title.text = grids_json[grid_id].title;
          var this_plot = jQuery(plot_html).appendTo('#fetchclimate_plot');
          this_plot.highcharts(high_chart);
          this_plot.attr('geometry', JSON.stringify({gridType:'CellGrid', gridData:grids_json[grid_id]}));
          this_plot.attr('variable', JSON.stringify({name:variable,sources:variables_json[variable]}));

        }
        for (var point_id in points_json) {
          high_chart.title.text = points_json[point_id].title;
          var this_plot = jQuery(plot_html).appendTo('#fetchclimate_plot');
          this_plot.highcharts(high_chart);
          this_plot.attr('geometry', JSON.stringify({gridType:'Points', gridData:points_json[point_id]}));
          this_plot.attr('variable', JSON.stringify({name:variable,sources:variables_json[variable]}));
        }
      }
    };

    //kills the ajax requests
    abortAllAjaxRequests = function() {
      m_all_ajax_requests.map(function(ajax_request) {
        ajax_request.abort();
      });
      m_all_ajax_requests = [];
    };

    //removes the high charts so there is no repitition
    removeHighCharts = function() {
      jQuery("#fetchclimate_plot .highcharts-plot").remove();
    };

    //shows the charts as loading
    addLoadingAttrToCharts = function() {
      var progress_bar_html =
          '<div class="progress plot-loading">'+
              '<div class="progress-bar progress-bar-striped" role="progressbar"' +
                ' aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;">Requesting:1/'+
                m_date_queries.length +'...</div>'+
          '</div>';
      var charts = jQuery("#fetchclimate_plot .highcharts-plot").each(function() {
        var chartHTML = jQuery(this).find('.highcharts-container');
        jQuery(progress_bar_html).appendTo(chartHTML);
        chartHTML.addClass('plot-parent');
        chartHTML.find('.highcharts-container').addClass('plot-overlay');
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
    m_public_interface = {
      initPlots: function(name) {
        //check if there is a map
        if(typeof FETCHCLIMATE_MAP !== 'undefined') {
          var map_changed = FETCHCLIMATE_MAP.getMapChanged();
        }
        else {
          map_changed = false;
        }
        //only do this if a change has been made
        if(FETCHCLIMATE_DATE.getDateChanged() || map_changed) {
          m_date_queries = FETCHCLIMATE_DATE.getQueries();
          m_date_query_sizes = FETCHCLIMATE_DATE.getQuerySizes();
          m_date_query_size = FETCHCLIMATE_DATE.getTotQuerySize();
          removeHighCharts();
          initHighCharts();
          addLoadingAttrToCharts();
        }
      },
      getData: function() {
        //check if there is a map
        if(typeof FETCHCLIMATE_MAP !== 'undefined') {
          var map_changed = FETCHCLIMATE_MAP.getMapChanged();
          FETCHCLIMATE_MAP.resetMapChanged();
        }
        else {
          map_changed = false;
        }
        //only do this if a change has been made
        if(FETCHCLIMATE_DATE.getDateChanged() || map_changed) {
          getPlotData();
          FETCHCLIMATE_DATE.resetDateChanged();
        }
      },
      getAllData: function() {
        if(m_request_complete) {
          return m_all_data;
        }
        return -1;
      }
    };

  /************************************************************************
     *                  INITIALIZATION / CONSTRUCTOR
     *************************************************************************/
    
    // Initialization: jQuery function that gets called when 
    // the DOM tree finishes loading
    $(function() {
      m_request_complete = false;
      m_all_ajax_requests = [];
    });

    return m_public_interface;

  }()); // End of package wrapper 
  // NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper 
  // function immediately after being parsed.
}
