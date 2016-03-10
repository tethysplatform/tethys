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
    var job_id = $(btn).attr('data-job-id');
    $(btn).on('click', function () {
        var execute_url = '/developer/gizmos/ajax/' + job_id + '/execute';
        $.ajax({
            url: execute_url
        }).done(function (json) {
            update_row($('#jobs-table-row-' + job_id));
        });
    });
}

function bind_delete_button(btn){
    btn = $(btn);
    var job_id = $(btn).attr('data-job-id');
    $(btn).on('click', function(){
        var delete_url = '/developer/gizmos/ajax/' + job_id + '/delete';
        $.ajax({
            url: delete_url
        }).done(function(json){
            if(json.success){
                row = $('#jobs-table-row-' + job_id);
                row.remove();
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

function update_row(table_elem){
    var table = $(table_elem).closest('table');
    var status_actions = $(table).attr('data-status-actions');
    var column_fields = $(table).attr('data-column-fields');
    var run = $(table).attr('data-run');
    var delete_btn = $(table).attr('data-delete');
    var results_url = $(table).attr('data-results-url');
    var refresh_interval = $(table).attr('data-refresh-interval');
    var job_id = $(table_elem).attr('data-job-id');
    var update_url = '/developer/gizmos/ajax/' + job_id + '/update-row';
    $.ajax({
        method: 'POST',
        url: update_url,
        data: {column_fields: column_fields, status_actions: status_actions, run: run, delete: delete_btn, results_url: results_url}
    }).done(function(json){
        if(json.success){
            $(table_elem).html(json.html);
            $(table_elem).find('.btn-job-run').each(function(){
                bind_run_button(this);
            });
            $(table_elem).find('.btn-job-delete').each(function(){
                bind_delete_button(this);
            });
            status = json.status;
            if(status == 'Running' || status == 'Submitted' || status == 'Various'){
                setTimeout(function(){
                    update_row(table_elem);
                }, refresh_interval);
            }
        }
    });
}


function update_status(table_elem){
    console.log(table_elem);
    var table = $(table_elem).closest('table');
    var status_actions = $(table).attr('data-status-actions');
    var run = $(table).attr('data-run');
    var delete_btn = $(table).attr('data-delete');
    var results_url = $(table).attr('data-results-url');
    var refresh_interval = $(table).attr('data-refresh-interval');
    var job_id = $(table_elem).attr('data-job-id');
    var update_url = '/developer/gizmos/ajax/' + job_id + '/update-status';
    $.ajax({
        method: 'POST',
        url: update_url,
        data: {status_actions: status_actions, run: run, delete: delete_btn, results_url: results_url}
    }).done(function(json){
    console.log(json);
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

$('.btn-job-run').each(function(){
    bind_run_button(this);
});

$('.btn-job-delete').each(function(){
    bind_delete_button(this);
});

$('.job-status').each(function(){
    console.log(this);
    update_status(this);
});