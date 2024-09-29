/*****************************************************************************
 *
 * Update job status with a timeout while job is still running.
 *
 *****************************************************************************/
function add_message(message, message_type='danger'){
  if(message){
    if(message_type == 'danger'){
      message = '<strong>Error!</strong> ' + message;
    }
    var alert_html = '<div class="alert alert-' + message_type + ' alert-dismissible" role="alert">' +
                         message +
                        '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>' +
                    '</div>';
    $('#jobs-table-messages').append(alert_html);
  }
}

const status_html =
'<div class="progress" style="margin-bottom: 0;">' +
    '<div class="progress-bar bg-warning progress-bar-striped progress-bar-animated" role="progressbar" title="Submitted" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%">' +
    '</div>' +
'</div>';

var base_ajax_url = "";
$('.jobs-table').each(function(){
  $table = $(this);
  base_ajax_url = $table.data('base-ajax-url');
});

function bind_action(action, on_success=()=>{}){
  if($(action).hasClass('disabled')){
    return;
  }
  var job_id = $(action).data('job-id');
  var label = $(action).text();
  var show_overlay = $(action).data('show-overlay');
  var confirmation_message = $(action).data('confirmation-message');
  var modal_url = $(action).data('modal-url');
  var callback = $(action).data('callback');
  var url = base_ajax_url + job_id + '/action/' + callback;
  var do_action = function () {
      if(show_overlay){
        $("#jobs_table_overlay").removeClass('d-none');
      }
      $(action).closest('td').prev().html(status_html);
      $.ajax({
          url: url
      }).done(function (json) {
          $("#jobs_table_overlay").addClass('d-none');
          update_row($('#jobs-table-row-' + job_id));
          if(json.success){
            on_success(job_id);
            add_message(json.message, message_type='success');
          }
          else{
            add_message(json.message)
          }
      });
  };

  if(callback){
    $(action).on('click', function(){
      if(confirmation_message){
        $('#modal-dialog-jobs-table-confirm-content').html(confirmation_message);
        $('#tethys_jobs-table-confirm').html(label);
        $('#tethys_jobs-table-confirm').off('click');
        $('#tethys_jobs-table-confirm').on('click', function(){
          do_action();
          $('#modal-dialog-jobs-table-confirm').modal('hide');
        });
      }
      else{
        do_action();
      }
    });
  }
}

var log_contents = {};

function load_log_content(job_id) {
    // Clear content
    $('#modal-dialog-jobs-table-log-content').html('');
    $("#jobs_table_logs_overlay").removeClass('d-none');

    $('#ModalJobLogTitle').html('Logs for Job ID: ' + job_id);
    var show_log_url = base_ajax_url + job_id + '/action/show-log';
    $.ajax({
        url: show_log_url
    }).done(function(json){
        if(json.success){
            log_contents = json.log_contents;
            $('#modal-dialog-jobs-table-log-nav').html(json.html);
            $('#modal-dialog-jobs-table-log-nav').find('.tethys-select2').select2();
            if ($('.jobs-table-log-menu').length > 0){
              $('#sub_job_select').on('change', update_log_menu);
              $('.jobs-table-log-menu').on('change', update_log_content);
            }
            else{
              $('#sub_job_select').on('change', update_log_content);
            }
            $('#sub_job_select').trigger('change');
        }
        else{
          $("#jobs_table_logs_overlay").addClass('d-none');
          $('#modal-dialog-jobs-table-log-content').html(json.error_message);
        }
    });
}

function update_log_menu(event){
  var key = event.target.value;
  $('.jobs-table-log-menu').addClass('d-none');
  $('#log_select_' + key).removeClass('d-none');
  $('#log_' + key).trigger('change');
}

function update_log_content(event, use_cache=true){
  var job_id = $('#sub_job_select').data('job-id');
  var key1 = $('#sub_job_select').val();
  var key2 = $('#log_' + key1).val();
  var content;
  var log_content_url = base_ajax_url + job_id + '/log-content/' + key1;
  if (key2 === undefined){
    content = log_contents[key1];
  }else{
    log_content_url += '/' + key2;
    content = log_contents[key1][key2];
  }

  if(use_cache && content != null){
    $("#jobs_table_logs_overlay").addClass('d-none');
    $('#modal-dialog-jobs-table-log-content').html(`<pre>${content}</pre>`);
  }
  else{
    $('#modal-dialog-jobs-table-log-content').html('');
    $("#jobs_table_logs_overlay").removeClass('d-none');

    $.ajax({
        url: log_content_url
    }).done(function(json){
    $("#jobs_table_logs_overlay").addClass('d-none');
      if(json.success){
        content = json.content;
        $('#modal-dialog-jobs-table-log-content').html(`<pre>${content}</pre>`);
        if (key2 === undefined){
          log_contents[key1] = content;
        }else{
          log_contents[key1][key2] = content;
        }
      }
      else{
        $('#modal-dialog-jobs-table-log-content').html(json.error_message);
      }
    });
  }
}

function bind_show_log_action(action){
    var job_id = $(action).data('job-id');
    $(action).on('click', function(){
        $('#modal-dialog-jobs-table-log-nav').html('');
        bind_log_refresh_button(job_id);
        load_log_content(job_id);
    });
}

function bind_log_refresh_button(job_id){
  var $btn = $("#tethys_log_refresh_job_id");
  $btn.val(job_id);
  $btn.on('click', function(){
        update_log_content(null, use_cache=false);
    });
}

function get_first_id_from_content(contents) {
    let first_id = '';
    let key1 = Object.keys(contents)[0];
    if (typeof(contents[key1] == 'string')) {
        first_id = `logfrom_${key1}`;
    }
    else {
        let key2 = Object.keys(contents[key1])[0];
        first_id = `logfrom_${key1}_${key2}`;
    }
    return first_id
}

function display_log_content(log_content_id) {
    // Hide all the class first
    $('.tethys_job_log_content').addClass('d-none');

    //Display the selected log
    $('#' + log_content_id).removeClass('d-none');
}

function render_workflow_nodes_graph(dag, target_selector) {
    // Create new graph with left-right orientation.
    let g = new dagreD3.graphlib.Graph()
        .setGraph({
            rankdir: "LR",
            ranksep: 100,
            nodesep: 20,
            marginx: 20,
            marginy: 20
        })
        .setDefaultEdgeLabel(function() { return {}; });

    // Setup nodes on the graph
    for (node_id in dag) {
        let node = dag[node_id];

        g.setNode(node_id, {
            label: node.display,
            class: "status-" + node.status,
            description: node.status
        });
    }

    // Post process nodes
    g.nodes().forEach(function(v) {
        var node = g.node(v);
        // Round corners of nodes
        node.rx = node.ry = 5;
    });

    // Setup edges on the graph using parent relationships
    for (node_id in dag) {
        let node = dag[node_id];
        let parents = node.parents;
        parents.forEach(function(parent_id) {
            g.setEdge(parent_id, node_id);
        });
    }

    // Setup SVG and group so we can translate the final graph.
    $(target_selector).html('<svg></svg><p class="loading-error">');
    let svg_selector = target_selector + " svg";
    let svg = d3.select(svg_selector);
    let inner = svg.append('g');
    let inner_selector = target_selector + " svg g"

    // Create the graph renderer
    let render = new dagreD3.render();
    render(d3.select(inner_selector), g);

    // Center the graph
    let min_height = 120;
    let x_center_offset = ($(svg_selector).width() - g.graph().width) / 2;
    let y_center_offset = (g.graph().height >= min_height) ? 0 : (min_height - g.graph().height) / 2;
    svg.attr("height", (g.graph().height >= min_height) ? g.graph().height : min_height);
    inner.attr("transform", "translate(" + x_center_offset + "," + y_center_offset + ")");

    // Create legend
    let legend_entries = [
        {"title": "Pending", "color": "#cccccc"},
        {"title": "Submitted", "color": "#f0ad4e"},
        {"title": "Running", "color": "#5bc0de"},
        {"title": "Complete", "color": "#5cb85c"},
        {"title": "Error", "color": "#d9534f"},
        {"title": "Aborted", "color": ""}
    ];

    let legend = svg.append("g")
        .attr("class", "legend")
        .attr("transform", "translate(15,20)");

    let legend_items = legend.append("g")
        .attr("class", "legend-items");

    for (var i = 0; i < legend_entries.length; i++) {
        let legend_entry = legend_entries[i];

        legend_items.append("text")
            .attr("x", "10px")
            .attr("y", i * 16 + "px")
            .text(legend_entry.title);

        legend_items.append("circle")
            .attr("r", "6px")
            .attr("cx", 0)
            .attr("cy", (i * 16) - 5 + "px")
            .style("fill", legend_entry.color);
    }
}

function update_row(table_elem){
    var table = $(table_elem).closest('table');
    var show_status = $(table).data('show-status');
    var show_actions = $(table).data('show-actions');
    var actions = $(table).data('actions');
    var column_fields = $(table).data('column-fields');
    var refresh_interval = $(table).data('refresh-interval');
    var job_id = $(table_elem).data('job-id');
    var update_url = base_ajax_url + job_id + '/update-row';
    var active_statuses = $(table).data('active-statuses');

    var data = {
        column_fields: column_fields,
        show_status: show_status,
        show_actions: show_actions,
        actions: actions,
    };
    $.ajax({
        method: 'POST',
        url: update_url,
        data: data
    }).done(function(json){
        if(json.success){
            var current_status = $('#jobs-table-status-'+job_id).children('div').attr('title') || 'None';
            if(current_status != json.status) {
                $(table_elem).html(json.html);
                bind_jobs_table_actions(table_elem);
                status = json.status;
            }

            if(active_statuses.includes(status)) {
                active_counter++;
                setTimeout(function(){
                    update_row(table_elem);
                }, refresh_interval);
            }
        } else {
            $(table_elem).html(json.html);
            bind_jobs_table_actions(table_elem);
        }
        $('[data-bs-toggle="tooltip"]').tooltip();
    });

    var next_row = $(table_elem).next('tr');

    if($(next_row).hasClass('workflow-nodes-row')){
      update_workflow_nodes_row(next_row);
    }
}

function bind_modal_url(action){
  var job_id = $(action).data('job-id');
  var modal_url = $(action).data('modal-url');
    $(action).on('click', function(){
    $.ajax({
        url: modal_url,
    }).done(function(response){
       $('#modal-dialog-jobs-table-modal-content').html(response)
      })
  });
}

function bind_jobs_table_actions(table_elem){
  $(table_elem).find('.job-action').each(function(){
    var action = $(this);
    if(action.hasClass('job-action-delete')){
      var on_success = function(job_id){
          row = $('#jobs-table-row-' + job_id);
          row.remove();
          workflow_row = $('#workflow-nodes-row-' + job_id);
          workflow_row.remove();

          // Delete bokeh row when delete row.
          $('#bokeh-nodes-row-' + job_id).html('');
      };
      bind_action(action, on_success);
    }
    else if(action.hasClass('job-action-view-logs')){
      bind_show_log_action(action);
    }
    else if(action.data('modal-url')){
      bind_modal_url(action);
    }
    else if(action.hasClass('job-action-refresh-status')){
        action.on('click', function(){
            update_row(table_elem);
        });
    }
    else{
      bind_action(action);
    }
  });
  format_time_fields();
}

function update_workflow_nodes_row(table_elem){
    var table = $(table_elem).closest('table');
    var refresh_interval = $(table).data('refresh-interval');
    var job_id = $(table_elem).data('job-id');
    var target_selector = "#" + $(table_elem).attr('id') + " td .workflow-nodes-graph";
    var error_selector = target_selector + ' .loading-error';
    var update_url = base_ajax_url + job_id + '/update-workflow-nodes-row';
    var active_statuses = $(table_elem).data('active-statuses');

    $.ajax({
        method: 'POST',
        url: update_url,
        data: {}
    }).done(function(json){
        if(json.success){
            // Clear errors
            $(error_selector).html('');

            // Render graph
            render_workflow_nodes_graph(json.dag, target_selector);

            // Update again?
            status = json.status;
            if(active_statuses.includes(status)){
                setTimeout(function(){
                    update_workflow_nodes_row(table_elem);
                }, refresh_interval);
            }
        }
        else
        {
            // Display error
            $(error_selector).html('An unexpected error occurred while updating. Trying again in '
                                   + refresh_interval / 1000 + ' seconds.');
            // Update again
            setTimeout(function(){
                update_workflow_nodes_row(table_elem);
            }, refresh_interval);
        }
    });
}

function bokeh_nodes_row(table_elem){
    var table = $(table_elem).closest('table');
    var refresh_interval = $(table).data('refresh-interval');
    var job_id = $(table_elem).data('job-id');
    // options for type is individual-graph, individual-progress and individual-task-stream for now
    var type = 'individual-progress';
    var update_url = base_ajax_url + job_id + '/' + type + '/insert-bokeh-row';

    $.ajax({
        method: 'POST',
        url: update_url,
        data: {}
    }).done(function(json){
        // Only show bokeh if we can find any jobs still running.
        if (active_counter > 0) {
            $('#bokeh-nodes-row-' + job_id).html(
                '<td id="job_id_' + job_id + '" colspan="100%">' +
                  '<div id="icon_job_id_' + job_id + '"><strong>Hide Details</strong></div>' +
                  '<div id="content_job_id_' + job_id + '">' + json.html + '</div>' +
                '</td>');

            // two click event has been binded to the element. use off() to unbind click event and then on() to bind it again.
            $('#bokeh-nodes-row-' + job_id).off('click').on('click', function() {
                var content_id = 'content_job_id_' + job_id;
                var icon_id = 'icon_job_id_' + job_id;
                var element = document.getElementById(content_id);
                var element_icon = document.getElementById(icon_id);
                if (element.style.display == "none") {
                    element.style.display = "block";
                    element_icon.innerHTML = '<strong>Hide Details</strong>';
                } else {
                    element.style.display = "none";
                    element_icon.innerHTML = '<strong>Show Details</strong>';
                }
            })
        }
    });
}

function init_data_table(){
    $('.jobs-table').each(function(){
        $table = $(this);
        var enable_data_table = $table.data('enable-data-table');
        if(enable_data_table){
            var options = $table.data('data-table-options');
            options.columnDefs = options.columnDefs || [];
            options.columnDefs.push({
              targets: 'no-sort',
              orderable: false,
            });

            $table.DataTable(options);
        }
    });
}

/*****************************************************************************
 *
 * Date Utils
 *
 *****************************************************************************/

function get_month_from_string(mon){
    return "Jan.Feb.Mar.Apr.May.Jun.Jul.Aug.Sep.Oct.Nov.Dec.".indexOf(mon) / 4;
};

function parse_datetime(date){
    var parts = date.split(/[\s,:]+/);

    var mon = get_month_from_string(parts[0].slice(0, 3) + '.');
    var day = parts[1];
    var year = parts[2];
    var hour = parseInt(parts[3]);
    var min = parts.length > 5 ? parts[4] : 0;
    if(parts[parts.length - 1] == 'p.m.'){
      hour += 12;
    }

    return new Date(Date.UTC(year, mon, day, hour, min));
}

function format_datetime(date){
    const options = {month: 'short', day: 'numeric', year: 'numeric', hour12: false, hour: 'numeric', minute: 'numeric'};
    return date.toLocaleString('en-US', options);
}

function format_time_fields(){
  ['creation', 'start', 'execute', 'completion'].forEach(function(name){
    $(`.${name}_time-field:not(.local-time)`).each(function(){
        $(this).addClass('local-time');
        var date_str = $(this).html();
        var date = parse_datetime(date_str);
        date_str = format_datetime(date);
        $(this).html(date_str);
    });
  });
}

/*****************************************************************************
 *
 * Initialization Code
 *
 *****************************************************************************/

init_data_table();

bind_jobs_table_actions($('.jobs-table'))

// Keep track of how many job are active. If none of the jobs are active, we won't show bokeh graph.
var active_counter = 0;

$('.job-row').each(function(){
    update_row(this);
});

// Only show bokeh for the top row.
var counter = 0;
$('.bokeh-nodes-row').each(function(){
    counter++;
    if (counter == 1) { bokeh_nodes_row(this);}
    else { return false;}
});
