/*****************************************************************************
 * FILE: fetchclimate_date.js
 * DATE: 8/6/2014
 * AUTHOR: Alan Snow
 * COPYRIGHT: (c) 2014 Brigham Young University
 * LICENSE: BSD 2-Clause
 *****************************************************************************/
//only include if there are no plots
if(jQuery('#fetchclimate_plot').length <= 0) {
  /*****************************************************************************
   *                      LIBRARY WRAPPER
   *****************************************************************************/
  var FETCHCLIMATE_DATA = (function() {
    // Wrap the library in a package function
    "use strict"; // And enable strict mode for this library
    
    /************************************************************************
     *                      MODULE LEVEL / GLOBAL VARIABLES
     *************************************************************************/
     var m_public_interface, // Object returned by the module
          m_date_queries, m_date_query_sizes, m_date_query_size, 
          m_service_url, m_all_data, m_request_complete, m_all_ajax_requests;

    /************************************************************************
     *                    PRIVATE FUNCTION DECLARATIONS
     *************************************************************************/
     var getNumPoints, getPercentage, giveStatusUpdate, getSingleRequestData, 
        fetchAllData, abortAllAjaxRequests;

     /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/
    //gives the percent complete
    getPercentage = function(series_indexes_received) {
      var tot_size_received = 0;
      series_indexes_received.map(function(index) {
        tot_size_received += m_date_query_sizes[index];
      });
      return 100*tot_size_received/m_date_query_size;
    };

    //gives the user the status update
    giveStatusUpdate = function(grid, variable_name, series_indexes_received) {
      var percentage = Math.round(getPercentage(series_indexes_received));
      var update_text = grid.gridData.title + ' ('+variable_name+')';
      var update_bar_text = percentage != 100 ? 'Requesting:'+percentage+'%'+'...':'Complete!';
      jQuery('#fetchclimate_data #'+ variable_name+ '_' +grid.gridType +'_'+ grid.gridData.id+' .progress-bar')
        .text(update_bar_text)
        .attr('aria-valuenow',percentage)
        .css('width', percentage + '%');
      console.log(update_text+': '+update_bar_text);
    };

    //gets data for each request
    getSingleRequestData = function(grid, variable, series_index) {
      var series_indexes_received = [];
      var ajax_url = jQuery('#fc_outer_container').attr('data-ajax-url');
      //Perform ajax request for each of the date queries
      var requests = m_date_queries.map(function(date_query, series_index) {
        return jQuery.ajax({
            type: "GET",
            url: ajax_url,
            dataType: "json",
            data: {
                    serviceUrl: m_service_url,
                    variable : JSON.stringify(variable), 
                    grid : JSON.stringify(grid),
                    time : JSON.stringify(date_query)
            },
            success: function(data) {
              series_indexes_received.push(series_index);
              console.log(grid.gridData.title + ' ('+variable.name+'): '+series_indexes_received.length+'/'+m_date_queries.length);
              giveStatusUpdate(grid,variable.name,series_indexes_received);
            }
        });
      });
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
        if (data.length>0) {
          m_all_data[variable.name][grid.gridData.title] = data;
        } else {
          m_all_data[variable.name][grid.gridData.title] = null;
        }
        var one_request_complete_event = new CustomEvent('fcOneDataRequestComplete', {'detail': {variable: variable, grid: grid, data: data}});
        jQuery('#fetchclimate_data')[0].dispatchEvent(one_request_complete_event);

      });
      return requests;
    };
    //intializes the highcharts before loading data
    fetchAllData = function() {
      //end any previous ajax calls
      abortAllAjaxRequests();

      jQuery('#fetchclimate_data').html('');
      m_request_complete = false;
      m_all_data = {};
      m_date_queries = FETCHCLIMATE_DATE.getQueries();
      m_date_query_sizes = FETCHCLIMATE_DATE.getQuerySizes();
      m_date_query_size = FETCHCLIMATE_DATE.getTotQuerySize();
      var serverURL = jQuery('#fc_outer_container').attr('data-server-url');
      m_service_url = serverURL.length>0?serverURL:'';
      var update_html = "";
      var progress_bar_html =
          '<div class="progress">'+
              '<div class="progress-bar progress-bar-striped" role="progressbar"' +
                ' aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;">Requesting:1/'+
                m_date_queries.length +'...</div>'+
          '</div>';
      if(typeof FETCHCLIMATE_MAP !== 'undefined') {
        var grids_json = FETCHCLIMATE_MAP.getGridsJSON();
        var points_json = FETCHCLIMATE_MAP.getPointsJSON();
      }
      else {
        var grids_json = JSON.parse(jQuery('#fc_outer_container').attr('data-grids'));
        var points_json = JSON.parse(jQuery('#fc_outer_container').attr('data-points'));
      }
      var variables_json = JSON.parse(jQuery('#fc_outer_container').attr('data-variables'));
      for (var variable in variables_json) {
        m_all_data[variable] = {};
        //loop through grids
        for (var grid_id in grids_json) {
          update_html = '<div id="'+variable+'_CellGrid_'+grid_id+'">'+
              grids_json[grid_id].title+' ('+variable+')'+ progress_bar_html + '</div>';
          jQuery(update_html).appendTo('#fetchclimate_data');
          grids_json[grid_id].id = grid_id;
          var grid_requests = getSingleRequestData(
            {
              gridType:'CellGrid', 
              gridData: grids_json[grid_id]
            },
            {
              name:variable,
              sources:variables_json[variable]
            });
        }
        //loop through points
        for (var point_id in points_json) {
          update_html = '<div id="'+variable+'_Points_'+point_id+'">'+ 
                        points_json[point_id].title+' ('+variable+')'+
                        progress_bar_html + '</div>';
          jQuery(update_html).appendTo('#fetchclimate_data');
          points_json[point_id].id = point_id;
          var point_requests = getSingleRequestData(
                        {
                          gridType:'Points', 
                          gridData:points_json[point_id]
                        },
                        {
                          name:variable,
                          sources:variables_json[variable]
                        });
        }
      }
      //When all of the requests are completed
      m_all_ajax_requests = grid_requests.concat(point_requests);
      jQuery.when.apply(jQuery, m_all_ajax_requests).then(function() {
        m_all_ajax_requests = [];
        console.log("Your request is complete. You can view the data in the console and you can access" +
          "the data through the Javascript API in the snippets documentation."); 
        jQuery('#fetchclimate_data .progress-bar').each(function() {
          jQuery(this)
            .css('width','100%')
            .attr('aria-valuenow',100)
            .addClass('progress-bar-success')
            .text('Complete!');
        });
        m_request_complete = true;
        var request_complete_event = new CustomEvent('fcDataRequestComplete', {'detail':m_all_data});
        jQuery('#fetchclimate_data')[0].dispatchEvent(request_complete_event);
      });
    };

    abortAllAjaxRequests = function() {
      m_all_ajax_requests.map(function(ajax_request) {
        ajax_request.abort();
      });
      m_all_ajax_requests = [];
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
      fetchAllData: function() {
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
          fetchAllData();
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
      // Initialize Global Variables
      m_request_complete = false;
      m_all_ajax_requests = [];
    });

    return m_public_interface;

  }()); // End of package wrapper 
  // NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper 
  // function immediately after being parsed.
}
