/*****************************************************************************
 *
 * Cross Site Request Forgery Token Configuration
 *   copied from (https://docs.djangoproject.com/en/1.7/ref/contrib/csrf/)
 *
 *****************************************************************************/

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

/*****************************************************************************
 *
 * Update job status with a timeout while job is still running.
 *
 *****************************************************************************/

function bind_run_button(btn){
    var job_id = $(btn).data('job-id');
    $(btn).on('click', function () {
        var execute_url = '/developer/gizmos/ajax/' + job_id + '/execute';
        $.ajax({
            url: execute_url
        }).done(function (json) {
            status_html =
            '<div class="progress" style="margin-bottom: 0;">' +
                '<div class="progress-bar progress-bar-warning progress-bar-striped active" role="progressbar" title="Submitted" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%">' +
                    '<span class="sr-only">100% Complete</span>' +
                '</div>' +
            '</div>'
            $(btn).parent().html(status_html);
            update_row($('#jobs-table-row-' + job_id));
        });
    });
}

function bind_refresh_button(btn){
    var job_id = $(btn).data('job-id');
    $(btn).on('click', function () {
        var execute_url = '/developer/gizmos/ajax/' + job_id + '/update-row';
        $.ajax({
            url: execute_url
        }).done(function (json) {
            status_html =
            '<div class="progress" style="margin-bottom: 0;">' +
                '<div class="progress-bar progress-bar-warning progress-bar-striped active" role="progressbar" title="Submitted" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%">' +
                    '<span class="sr-only">100% Complete</span>' +
                '</div>' +
            '</div>'
            $(btn).parent().html(status_html);
            update_row($('#jobs-table-row-' + job_id));
        });
    });
}

function bind_terminate_button(btn){
    var job_id = $(btn).data('job-id');
    $(btn).on('click', function(){
        $('#modal-dialog-jobs-table-confirm-content').html('Are you sure you want to terminate this job');
        $('#tethys_jobs-table-confirm').html('Terminate');
        $('#tethys_jobs-table-confirm').off('click');
        $('#tethys_jobs-table-confirm').on('click', function(){
            $("#jobs_table_overlay").removeClass('hidden');
            $('#modal-dialog-jobs-table-confirm').modal('hide');
            var delete_url = '/developer/gizmos/ajax/' + job_id + '/terminate';
            $.ajax({
                url: delete_url
            }).done(function(json){
                $("#jobs_table_overlay").addClass('hidden');
                if(json.success){
                    update_row($('#jobs-table-row-' + job_id));
                }
                else{
                    var alert_html = '<div class="alert alert-danger alert-dismissible" role="alert">' +
                                        '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' +
                                        '<strong>Error!</strong> Unable to terminate job ' + job_id + '.' +
                                    '</div>';
                    $('#jobs-table-messages').append(alert_html);
                }
            });
         });
    });
}

function bind_delete_button(btn){
    var job_id = $(btn).data('job-id');
    $(btn).on('click', function(){
        $('#modal-dialog-jobs-table-confirm-content').html('Are you sure you want to permanently delete this job?');
        $('#tethys_jobs-table-confirm').html('Delete');
        $('#tethys_jobs-table-confirm').off('click');
        $('#tethys_jobs-table-confirm').on('click', function(){
            $("#jobs_table_overlay").removeClass('hidden');
            $('#modal-dialog-jobs-table-confirm').modal('hide');
            var delete_url = '/developer/gizmos/ajax/' + job_id + '/delete';
            $.ajax({
                url: delete_url
            }).done(function(json){
                $("#jobs_table_overlay").addClass('hidden');
                if(json.success){
                    row = $('#jobs-table-row-' + job_id);
                    row.remove();
                    workflow_row = $('#workflow-nodes-row-' + job_id);
                    workflow_row.remove();

                    // Delete bokeh row when delete row.
                    $('#bokeh-nodes-row-' + job_id).html('');
                }
                else{
                    var alert_html = '<div class="alert alert-danger alert-dismissible" role="alert">' +
                                        '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' +
                                        '<strong>Error!</strong> Unable to delete job ' + job_id + '.' +
                                    '</div>';
                    $('#jobs-table-messages').append(alert_html);
                }
            });
         });
    });
}

function bind_resubmit_button(btn){
    var job_id = $(btn).data('job-id');
    $(btn).on('click', function(){
        $("#jobs_table_overlay").removeClass('hidden');
        var resubmit_url = '/developer/gizmos/ajax/' + job_id + '/resubmit';
        $.ajax({
            url: resubmit_url
        }).done(function(json){
            update_row($(btn).closest('tr'));
            $("#jobs_table_overlay").addClass('hidden');
            if(json.success){
                var alert_html = '<div class="alert alert-success alert-dismissible" role="alert">' +
                                    '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' +
                                    '<strong>Successfully resubmit job: ' + job_id + '.' +
                                '</div>';
            }
            else{
                var alert_html = '<div class="alert alert-danger alert-dismissible" role="alert">' +
                                    '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' +
                                    '<strong>Error!</strong> Unable to resubmit job ' + job_id + '.' +
                                '</div>';
            }
            $('#jobs-table-messages').append(alert_html);
        });
    });
}

function load_log_content(job_id) {
    var show_log_url = '/developer/gizmos/ajax/' + job_id + '/show-log';
        $.ajax({
            url: show_log_url
        }).done(function(json){
            if(json.success){
                var contents = json.data;
                var log_html = generate_log_html(contents);
                $('#modal-dialog-jobs-table-log-nav').html(log_html.nav_header_html);
                $('#modal-dialog-jobs-table-log-content').html(log_html.nav_content_html);
                $('.tethys_job_log_content').hide();
                // Show the first log
                var first_content_id = get_first_id_from_content(contents);
                $(`#${first_content_id}`).show();
            }
        });
}

function bind_show_log_button(btn){
    var job_id = $(btn).data('job-id');
    $(btn).on('click', function(){
        load_log_content(job_id);
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

function generate_log_html(contents){
  var nav_header_html = "";
  var nav_content_html = "";

  nav_header_html += "<nav class='navbar navbar-default' style='border:0'><div class='container-fluid'><ul class='nav navbar-nav'>";
  $.each( contents, function(key, value) {
        key = key.replace('.', '_');
        // Create a nav if content is string
        if (typeof(value) == "string" || value == null ) {
            nav_header_html += "<li><a href='#' onclick=display_log_content('logfrom_" + key + "')>" + key + "</a></li>";
            nav_content_html += "<div class='tethys_job_log_content' id='logfrom_" + key + "'>" + value + "</div>";
        }
        else {
            nav_header_html += "<li class='dropdown'><a href='#' class='dropdown-toggle' data-toggle='dropdown' role='button' aria-haspopup='true' aria-expanded='false'>" + key + "<span class='caret'></span></a><ul class='dropdown-menu'>";
            $.each( value, function(key2, value2) {
                nav_header_html += "<li><a href='#' onclick=display_log_content('logfrom_" + key + "_" + key2 + "')>" + key2 + "</a></li>";
                nav_content_html += "<div class='tethys_job_log_content' id='logfrom_" + key + "_" + key2 +"'>" + value2 + "</div>";
            });
            nav_header_html += "</ul></li>";
            nav_content_html += "</ul></li>";
        }
    })
    nav_header_html +="</ul></div></nav>";
    return {'nav_header_html': nav_header_html, 'nav_content_html': nav_content_html};
}

function display_log_content(log_content_id) {
    // Hide all the class first
    $('.tethys_job_log_content').hide();

    //Display the selected log
    $('#' + log_content_id).show();
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
        .attr("transform", "translate(30,30)");

    let legend_items = legend.append("g")
        .attr("class", "legend-items");

    for (var i = 0; i < legend_entries.length; i++) {
        let legend_entry = legend_entries[i];

        legend_items.append("text")
            .attr("x", "1em")
            .attr("y", i + "em")
            .text(legend_entry.title);

        legend_items.append("circle")
            .attr("r", "0.4em")
            .attr("cx", 0)
            .attr("cy", i - 0.35 + "em")
            .style("fill", legend_entry.color);
    }
}

function update_row(table_elem){
    var table = $(table_elem).closest('table');
    var show_status = $(table).data('show-status');
    var show_actions = $(table).data('show-actions');
    var actions = $(table).data('actions');
    var column_fields = $(table).data('column-fields');
    var run = $(table).data('run');
    var delete_btn = $(table).data('delete');
    var resubmit_btn = $(table).data('resubmit');
    var show_log_btn = $(table).data('show-log')
    var results_url = $(table).data('results-url');
    var monitor_url = $(table).data('monitor-url');
    var refresh_interval = $(table).data('refresh-interval');
    var job_id = $(table_elem).data('job-id');
    var update_url = '/developer/gizmos/ajax/' + job_id + '/update-row';

    $.ajax({
        method: 'POST',
        url: update_url,
        data: {column_fields: column_fields, show_status: show_status, show_actions: show_actions, run: run, delete: delete_btn, monitor_url: monitor_url, show_resubmit_btn: resubmit_btn, show_log_btn: show_log_btn, results_url: results_url, actions: actions}
    }).done(function(json){
        if(json.success){
            var current_status = $('#jobs-table-status-'+job_id).children('div').attr('title') || 'None'
            if(current_status != json.status) {
                $(table_elem).html(json.html);
                bind_jobs_table_actions(table_elem);
                status = json.status;
            }

            if(status == 'Running' || status == 'Submitted' || status == 'Various') {
                active_counter++;
                setTimeout(function(){
                    update_row(table_elem);
                }, refresh_interval);
            }
        } else {
            $(table_elem).html(json.html);
            bind_jobs_table_actions(table_elem);
        }
    });
}

function bind_jobs_table_actions(table_elem){
  $(table_elem).find('.btn-job-run').each(function(){
      bind_run_button(this);
  });
  $(table_elem).find('.btn-job-terminate').each(function(){
      bind_terminate_button(this);
  });
  $(table_elem).find('.btn-job-delete').each(function(){
      bind_delete_button(this);
  });
  $(table_elem).find('.btn-job-resubmit').each(function(){
      bind_resubmit_button(this);
  });
  $(table_elem).find('.btn-job-show-log').each(function(){
      bind_show_log_button(this);
  });
  $(table_elem).find('.btn-refresh-status').each(function(){
      bind_refresh_button(this);
  });
  format_time_fields();
}

function update_workflow_nodes_row(table_elem){
    var table = $(table_elem).closest('table');
    var refresh_interval = $(table).data('refresh-interval');
    var job_id = $(table_elem).data('job-id');
    var target_selector = "#" + $(table_elem).attr('id') + " td .workflow-nodes-graph";
    var error_selector = target_selector + ' .loading-error';
    var update_url = '/developer/gizmos/ajax/' + job_id + '/update-workflow-nodes-row';

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
            if(status == 'Running' || status == 'Submitted' || status == 'Various'){
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
    var update_url = '/developer/gizmos/ajax/' + job_id + '/' + type + '/insert-bokeh-row';

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

    var mon = get_month_from_string(parts[0]);
    var day = parts[1];
    var year = parts[2];
    var hour = parseInt(parts[3]);
    var min = parts[4];
    if(parts[5] == 'p.m.'){
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

$('.workflow-nodes-row').each(function(){
    update_workflow_nodes_row(this);
});

// Assign job_id to load button
$(document).on('click', '.btn-job-show-log', function () {
    $('#modal-dialog-jobs-table-log-nav').html("");
    $('#modal-dialog-jobs-table-log-content').html("<p>Loading logs...</p>");
    var refresh_job_id = $(this).data('job-id');
    $("#tethys_log_refresh_job_id").val(refresh_job_id);
})

// Reload log content
$(document).on('click', '#tethys_log_refresh_job_id', function () {
    var refresh_job_id = $(this).val();

    // Clear content
    $('#modal-dialog-jobs-table-log-content').html("<p>Refreshing...</p>")

    // Load new content
    load_log_content(refresh_job_id);
})


// Only show bokeh for the top row.
var counter = 0;
$('.bokeh-nodes-row').each(function(){
    counter++;
    if (counter == 1) { bokeh_nodes_row(this);}
    else { return false;}
});
