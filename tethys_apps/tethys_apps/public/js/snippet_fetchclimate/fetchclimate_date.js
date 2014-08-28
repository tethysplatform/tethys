/*****************************************************************************
 * FILE:   fetchclimate_date.js
 * DATE: 7/25/2014   
 * AUTHOR: Alan Snow
 * COPYRIGHT: (c) 2014 Brigham Young University
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var FETCHCLIMATE_DATE = (function() {
  // Wrap the library in a package function
  "use strict"; // And enable strict mode for this library
  
  /************************************************************************
   *                      MODULE LEVEL / GLOBAL VARIABLES
   *************************************************************************/
   var m_public_interface,      // Object returned by the module
      m_date_changed, m_start_date, m_end_date, m_queries, 
      m_year_cell_mode, m_day_cell_mode, m_hour_cell_mode, m_query_size;
  /************************************************************************
   *                    PRIVATE FUNCTION DECLARATIONS
   *************************************************************************/
   var initArray, dayOfYear, updateDatePicker, updateDateJSON;
   /************************************************************************
   *                    PRIVATE FUNCTION IMPLEMENTATIONS
   *************************************************************************/
   initArray = function(lowEnd, highEnd) {
    var array = [];
    var c = highEnd - lowEnd + 1;
    while ( c-- ) {
     array[c] = highEnd--;
    }
    if (array.length == 1) {
      array = [array[0],array[0]];    
    }
    return array
  };

  dayOfYear = function(date) {
    var start = new Date(date.getFullYear(), 0, 0);
    var diff = date - start;
    var oneDay = 1000 * 60 * 60 * 24;
    return Math.ceil(diff / oneDay);  
  };

  updateDateJSON = function() {
    var start_date_val = jQuery('input#fc_start_date').val().split("/");
    var new_start_date = new Date(start_date_val[2],start_date_val[0]-1,start_date_val[1]);
    if(new_start_date.getTime() != (m_start_date?m_start_date.getTime():0)) {
      m_start_date = new_start_date;
      m_date_changed = true;
    }
    var end_date_val = jQuery('input#fc_end_date').val().split("/");
    var new_end_date = new Date(end_date_val[2],end_date_val[0]-1,end_date_val[1]);
    if(new_end_date.getTime() != (m_end_date?m_end_date.getTime():0)) {
      m_end_date = new_end_date;
      m_date_changed = true;
    }

    var new_year_cell_mode = jQuery('select#fc_year_mode').val() == 'avg';
    if(new_year_cell_mode != m_year_cell_mode) {
      m_year_cell_mode = new_year_cell_mode;
      m_date_changed = true;
    }
    var new_day_cell_mode = jQuery('select#fc_day_mode').val() == 'avg';
    if(new_day_cell_mode != m_day_cell_mode) {
      m_day_cell_mode = new_day_cell_mode;
      m_date_changed = true;
    }
    var new_hour_cell_mode = jQuery('select#fc_hour_mode').val() == 'avg';
    if(new_hour_cell_mode != m_hour_cell_mode) {
      m_hour_cell_mode = new_hour_cell_mode;
      m_date_changed = true;
    }
    var fc_years, fc_days, fc_hours, year_start, year_end;
    //run only if the dates are set correctly
    if (m_end_date>=m_start_date) {
      m_query_size = [1];
      year_start = m_start_date.getFullYear();
      year_end = m_end_date.getFullYear();
      fc_years = (m_year_cell_mode?[year_start,year_end]:initArray(year_start,year_end));
      if(m_hour_cell_mode) {
        fc_hours = [0,24];
      }
      else {
        fc_hours = [0,23];
        m_query_size = [24];
      }
      //CASE 1 - same year (Yay! all is well)
      if(year_end-year_start==0) {
        m_year_cell_mode = false; //cannot do average of years with only one year
        var start_day = dayOfYear(m_start_date);
        var end_day = dayOfYear(m_end_date);
        if(m_day_cell_mode) {
          fc_days = [1,365];
        }
        else {
          fc_days = (start_day==end_day?[start_day]:[start_day,end_day]);
          m_query_size[0] *= (end_day-start_day+1);
        }
        m_queries= [{
                    years:[fc_years[0]], yc:m_year_cell_mode, 
                    days:fc_days, dc:m_day_cell_mode,
                    hours:fc_hours, hc:m_hour_cell_mode
                }];
      }
      //CASE 2 - 2 different years (Oh well, two queries)
      else if (year_end-year_start == 1) {
        if(m_year_cell_mode) {
          // include all days of year if year cell mode
          m_queries= [{
                      years:fc_years, yc:m_year_cell_mode, 
                      days:[1,365], dc:m_day_cell_mode,
                      hours:fc_hours, hc:m_hour_cell_mode
                  }];
        }
        else {
          m_query_size.push(m_query_size[0]);
          var start_day_1 = dayOfYear(m_start_date); 
          var end_day_1 = dayOfYear(new Date(fc_years[0],11,31));
          var start_day_2 = 1;
          var end_day_2 = dayOfYear(m_end_date);
          if(m_day_cell_mode) {
            //add a day if only one day in the year in day cell mode
            fc_days = [(start_day_1==end_day_1?[end_day_1-1,end_day_1]:[start_day_1,end_day_1]),
                      (start_day_2==end_day_2?[start_day_2,start_day_2+1]:[start_day_2,end_day_2])];
          } 
          else {
            fc_days = [(start_day_1==end_day_1?[start_day_1]:[start_day_1,end_day_1]),
                      (start_day_2==end_day_2?[start_day_2]:[start_day_2,end_day_2])];
            m_query_size[0] *= (end_day_1-start_day_1+1);
            m_query_size[1] *= (end_day_2-start_day_2+1);
          }
          m_queries= [
                    {years:[fc_years[0]], yc:m_year_cell_mode, 
                    days:fc_days[0], dc:m_day_cell_mode, 
                    hours:fc_hours, hc:m_hour_cell_mode
                    },
                    {years:[fc_years[1]], yc:m_year_cell_mode, 
                    days:fc_days[1], dc:m_day_cell_mode, 
                    hours:fc_hours, hc:m_hour_cell_mode
                  }];
        }
      }
      //CASE 3 - more than two years (Oh man, three queries)
      else {
        if(m_year_cell_mode) {
          // include all days of year if year cell mode
          m_queries= [{
                      years:[fc_years[0],fc_years[fc_years.length-1]], yc:m_year_cell_mode, 
                      days:[1,365], dc:m_day_cell_mode,
                      hours:fc_hours, hc:m_hour_cell_mode
                  }];
        }
        else {
          m_query_size = [m_query_size[0],(m_query_size[0]*fc_years[fc_years.length-2]-fc_years[1]),m_query_size[0]];
          var start_day_1 = dayOfYear(m_start_date);
          var end_day_1 = dayOfYear(new Date(fc_years[0],11,31));
          var start_day_2 = 1;
          var end_day_2 = dayOfYear(new Date(fc_years[fc_years.length-2],11,31));
          var start_day_3 = 1;
          var end_day_3 = dayOfYear(m_end_date);
          if(m_day_cell_mode) {
            //include all days of the year
            fc_days = [[1,365],[1,365],[1,365]];
          }
          else {
            fc_days = [(start_day_1==end_day_1?[start_day_1]:[start_day_1,end_day_1]),
                      [start_day_2,end_day_2],
                      (start_day_3==end_day_3?[start_day_3]:[start_day_3,end_day_3])];
              m_query_size[0] *= (end_day_1-start_day_1+1);
              m_query_size[1] *= (end_day_2-start_day_2+1);
              m_query_size[2] *= (end_day_3-start_day_3+1);
          }
          m_queries= [
                {years:[fc_years[0]], yc:m_year_cell_mode, 
                days:fc_days[0], dc:m_day_cell_mode, 
                hours:fc_hours, hc:m_hour_cell_mode
                },
                {years:[fc_years[1],fc_years[fc_years.length-2]], yc:m_year_cell_mode, 
                days:fc_days[1], dc:m_day_cell_mode, 
                hours:fc_hours, hc:m_hour_cell_mode
                },
                {years:[fc_years[fc_years.length-1],fc_years[fc_years.length-1]], yc:m_year_cell_mode, 
                days:fc_days[2], dc:m_day_cell_mode, 
                hours:fc_hours, hc:m_hour_cell_mode
              }];
        }
      }
      jQuery('#fc_outer_container').attr('data-date',JSON.stringify(m_queries));
    }
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
    getQueries: function() {
      return m_queries;
    },
    getDateChanged: function() {
      return m_date_changed;
    },
    resetDateChanged: function() {
      m_date_changed=false;
    },
    getQuerySizes: function(index) {
      return m_query_size;
    },
    getTotQuerySize: function() {
      var tot_size = 0;
      m_query_size.map(function(query_size) {
        tot_size += query_size;
      });
      return tot_size;
    }
  };
  
  /************************************************************************
   *                  INITIALIZATION / CONSTRUCTOR
   *************************************************************************/
  
  // Initialization: jQuery function that gets called when 
  // the DOM tree finishes loading
  $(function() {
    m_date_changed = false; //keeps track of if there are changes 
    var FCdatePicker = jQuery('#fc_datepicker').datepicker({
      todayBtn: "linked",
      format:"mm/dd/yyyy",
      startDate: new Date(1800,1,1),
      endDate: new Date()
    })
    .on('changeDate', function(e) {
      updateDateJSON();
    });

    jQuery('select#fc_year_mode').change(function() {
      updateDateJSON();
    });
    jQuery('select#fc_day_mode').change(function() {
      updateDateJSON();
    });
    jQuery('select#fc_hour_mode').change(function() {
      updateDateJSON();
    });
    updateDateJSON();
  });

  return m_public_interface;

}()); // End of package wrapper 
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper 
// function immediately after being parsed.
