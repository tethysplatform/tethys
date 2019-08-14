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
    var results_url = $(table).data('results-url');
    var refresh_interval = $(table).data('refresh-interval');
    var job_id = $(table_elem).data('job-id');
    var update_url = '/developer/gizmos/ajax/' + job_id + '/update-row';
    $.ajax({
        method: 'POST',
        url: update_url,
        data: {column_fields: column_fields, status_actions: status_actions, run: run, delete: delete_btn, results_url: results_url}
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
        }
    });
}


function update_status(table_elem){
    var table = $(table_elem).closest('table');
    var status_actions = $(table).data('status-actions');
    var run = $(table).data('run');
    var delete_btn = $(table).data('delete');
    var results_url = $(table).data('results-url');
    var refresh_interval = $(table).data('refresh-interval');
    var job_id = $(table_elem).data('job-id');
    var update_url = '/developer/gizmos/ajax/' + job_id + '/update-status';
    $.ajax({
        method: 'POST',
        url: update_url,
        data: {status_actions: status_actions, run: run, delete: delete_btn, results_url: results_url}
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
// Keep track of how many job are active. If none of the jobs are active, we won't show bokeh graph.
var active_counter = 0;

$('.job-row').each(function(){
    update_row(this);
});

$('.workflow-nodes-row').each(function(){
    update_workflow_nodes_row(this);
});

// Only show bokeh for the top row.
var counter = 0;
$('.bokeh-nodes-row').each(function(){
    counter++;
    if (counter == 1) { bokeh_nodes_row(this);}
    else { return false;}
});