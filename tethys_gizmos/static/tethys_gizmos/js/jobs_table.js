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
    btn = $(btn);
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
    btn = $(btn);
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

function bind_delete_button(btn){
    btn = $(btn);
    var job_id = $(btn).data('job-id');
    $(btn).on('click', function(){
        var delete_url = '/developer/gizmos/ajax/' + job_id + '/delete';
        $.ajax({
            url: delete_url
        }).done(function(json){
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
}

function bind_resubmit_button(btn){
    btn = $(btn);
    var job_id = $(btn).data('job-id');
    $(btn).on('click', function(){
        $("#jobs_table_overlay").removeClass('hidden');
        var resubmit_url = '/developer/gizmos/ajax/' + job_id + '/resubmit';
        $.ajax({
            url: resubmit_url
        }).done(function(json){
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
                var nav_header = generate_nav_header(contents);
                $('#modal-dialog-jobs-table-log-nav').html(nav_header);
                var nav_contents = generate_nav_content(contents);
                $('#modal-dialog-jobs-table-log-content').html(nav_contents);
                $('.tethys_job_log_content').hide();
                // Show the first log
                var first_content_id = get_first_id_from_content(contents);
                $(`#${first_content_id}`).show();
            }
        });
}

function bind_show_log_button(btn){
    btn = $(btn);
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

function generate_nav_header(contents) {
    var nav_header_html = "";
    nav_header_html += "<nav class='navbar navbar-default' style='border:0'><div class='container-fluid'><ul class='nav navbar-nav'>";
    $.each( contents, function(key, value) {
        // Create a nav if content is string
        if (typeof(value) == "string" || value == null ) {
            nav_header_html += "<li><a href='#' onclick=display_log_content('logfrom_" + key + "')>" + key + "</a></li>";
        }
        else {
            nav_header_html += "<li class='dropdown'><a href='#' class='dropdown-toggle' data-toggle='dropdown' role='button' aria-haspopup='true' aria-expanded='false'>" + key + "<span class='caret'></span></a><ul class='dropdown-menu'>";
            $.each( value, function(key2, value2) {
                nav_header_html += "<li><a href='#' onclick=display_log_content('logfrom_" + key + "_" + key2 + "')>" + key2 + "</a></li>";
            });
            nav_header_html += "</ul></li>";
        }
    })
    nav_header_html +="</ul></div></nav>";
    return nav_header_html;
}

function generate_nav_content(contents) {
    var nav_content_html = "";
    $.each( contents, function(key, value) {
        // Create a nav if content is string
        if (typeof(value) == "string") {
            nav_content_html += "<div class='tethys_job_log_content' id='logfrom_" + key + "'>" + value + "</div>";
        }
        else {
            $.each( value, function(key2, value2) {
                nav_content_html += "<div class='tethys_job_log_content' id='logfrom_" + key + "_" + key2 +"'>" + value2 + "</div>";
            });
            nav_content_html += "</ul></li>";
        }
    })
    return nav_content_html;
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
    var status_actions = $(table).data('status-actions');
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
        data: {column_fields: column_fields, status_actions: status_actions, run: run, delete: delete_btn, monitor_url: monitor_url, show_resubmit_btn: resubmit_btn, show_log_btn: show_log_btn, results_url: results_url}
    }).done(function(json){
        if(json.success){
            var current_status = $('#jobs-table-status-'+job_id).children('div').attr('title') || 'None'
            if(current_status != json.status) {
                $(table_elem).html(json.html);
                $(table_elem).find('.btn-job-run').each(function(){
                    bind_run_button(this);
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
            $(table_elem).find('.btn-refresh-status').each(function(){
                bind_refresh_button(this);
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
        }
    });
}


function update_status(table_elem){
    var table = $(table_elem).closest('table');
    var status_actions = $(table).data('status-actions');
    var run = $(table).data('run');
    var delete_btn = $(table).data('delete');
    var resubmit_btn = $(table).data('resubmit');
    var results_url = $(table).data('results-url');
    var refresh_interval = $(table).data('refresh-interval');
    var job_id = $(table_elem).data('job-id');
    var update_url = '/developer/gizmos/ajax/' + job_id + '/update-status';
    $.ajax({
        method: 'POST',
        url: update_url,
        data: {status_actions: status_actions, run: run, delete: delete_btn, show_resubmit_btn: resubmit_btn, results_url: results_url}
    }).done(function(json){
        if(json.success){
            $(table_elem).html(json.html);
            status = json.status;
            if(status == 'Running' || status == 'Submitted' || status == 'Various'){
                setTimeout(function(){
                    update_status(table_elem);
                }, refresh_interval);
            }
        }
    });
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


$('.btn-refresh-status').each(function(){
    bind_refresh_button(this);
});

$('.btn-job-run').each(function(){
    bind_run_button(this);
});

$('.btn-job-delete').each(function(){
    bind_delete_button(this);
});

$('.btn-job-resubmit').each(function(){
    bind_resubmit_button(this);
});

$('.btn-job-show-log').each(function(){
    bind_show_log_button(this);
});
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
    $('#modal-dialog-jobs-table-log-content').html("<p>Loading logs...</p>");
    var refresh_job_id = $(this).data('job-id');
    $("#tethys_log_refresh_job_id").val(refresh_job_it);
})

// Reload log content
$(document).on('click', '#tethys_log_refresh_job_id', function () {
    var refresh_job_id = $(this).val();

    // Clear content
    $('#modal-dialog-jobs-table-log-content').html("<p>Refreshing...</p>")

    // Load new content
    load_log_content(refresh_job_it);
})


// Only show bokeh for the top row.
var counter = 0;
$('.bokeh-nodes-row').each(function(){
    counter++;
    if (counter == 1) { bokeh_nodes_row(this);}
    else { return false;}
});