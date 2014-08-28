jQuery(window).load(function() {
  jQuery('#fc_next_step_button').click(function() {
    //Order of 'if statement' matters because the map is not always there
    //This is if they are on the date picker step
    if (!jQuery('#fetchclimate_date').hasClass('hidden')) {
      if(typeof FETCHCLIMATE_MAP !== 'undefined') {
        var map_changed = FETCHCLIMATE_MAP.getMapChanged();
      }
      else {
        map_changed = false;
      }
      var go_ahead = true;
      //only do this if a change has been made
      if(FETCHCLIMATE_DATE.getDateChanged() || map_changed) {
        //check size of data request
        var query_size = FETCHCLIMATE_DATE.getTotQuerySize();
        if(query_size>1000) {
          go_ahead = confirm('You have a large data query size (Data size: ' + query_size +
            '). This could take a long time. Would you like to continue?');
        }
      }
      if(go_ahead) {
        //make sure the plot exists
        if(jQuery('#fetchclimate_plot').length !== 0) {
          jQuery('#fc_next_step_button').text('Loading...');
          FETCHCLIMATE_PLOT.initPlots(); 
          jQuery('#fc_next_step_button').html('<i class="icon-play"></i>Next Step');
          FETCHCLIMATE_PLOT.getData(); 
        }
        else {
          FETCHCLIMATE_DATA.fetchAllData();
        }
        jQuery('#fetchclimate_data').removeClass('hidden');
        jQuery('#fetchclimate_plot').removeClass('hidden');
        jQuery('#fc_next_step_button').addClass('hidden');
        jQuery('#fc_prev_step_button').removeClass('hidden');
        jQuery('#fetchclimate_date').addClass('hidden');
      }
    }
    //This should only occur if there was a map and it was the first step
    else if(!jQuery('#fetchclimate_map').hasClass('hidden')) {
      jQuery('#fetchclimate_map').addClass('hidden');
      jQuery('#fetchclimate_date').removeClass('hidden');
      jQuery('#fc_prev_step_button').removeClass('hidden');
    }
  });

  jQuery('#fc_prev_step_button').click(function() {
    //This is if they are going back a step from the date picker  
    if (!jQuery('#fetchclimate_date').hasClass('hidden')) {
      jQuery('#fc_prev_step_button').addClass('hidden');
      jQuery('#fetchclimate_date').addClass('hidden');
      jQuery('#fetchclimate_map').removeClass('hidden');
    } 
    //This is if they are going back a step from the plot/data
    else if (!jQuery('#fetchclimate_plot').hasClass('hidden')) {
      jQuery('#fetchclimate_plot').addClass('hidden');
      jQuery('#fc_next_step_button').removeClass('hidden');
      jQuery('#fetchclimate_date').removeClass('hidden');
      //if the map is not included in options
      if(jQuery('#fetchclimate_map').length ==0) {
        jQuery('#fc_prev_step_button').addClass('hidden');
      }
      //if there is data
      if(!jQuery('#fetchclimate_data').hasClass('hidden')) {
        jQuery('#fc_next_step_button').text('Finish');
        jQuery('#fetchclimate_data').addClass('hidden');
      }
    }
  });

  //add event listener for when data addition is complete
  if(jQuery('#fetchclimate_data').length > 0) {
    jQuery('#fetchclimate_data')[0].addEventListener('fcDataRequestComplete', function(e) { 
      console.log(e.detail);
    });
    jQuery('#fetchclimate_data')[0].addEventListener('fcOneDataRequestComplete', function(e) { 
      console.log(e.detail);
    });
  }
  if(jQuery('#fetchclimate_plot').length > 0) {
    jQuery('#fetchclimate_plot')[0].addEventListener('fcDataRequestComplete', function(e) { 
      console.log(e.detail);
    });
    jQuery('#fetchclimate_plot')[0].addEventListener('fcOneDataRequestComplete', function(e) { 
      console.log(e.detail);
    });
  }
});
