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

function update_status(table_elem){
    var job_id = $(table_elem).attr('data-job-id');
    var results_url = $(table_elem).attr('data-results-url');
    var run = $(table_elem).attr('data-run');
    var filters = $(table_elem).closest('table').attr('data-col-filters');
    var update_url = '/developer/gizmos/ajax/' + job_id + '/update-status';
    $.ajax({
        method: 'POST',
        url: update_url,
        data: {results_url: results_url, run: run}
    }).done(function(json){
        if(json.success){
            table_elem = $(table_elem).html(json.html);
            status = json.status;
            if(status == 'Running' || status == 'Submitted' || status == 'Various'){
                setTimeout(function(){
                    update_status(table_elem);
                }, 4000);
            }
        }
    });
}

function update_row(table_elem){
    var table = $(table_elem).closest('table');
    var results_url = $(table).attr('data-results-url');
    var run = $(table).attr('data-run');
    var status = $(table).attr('data-status');
    var actions = $(table).attr('data-actions');
    var filters = $(table).attr('data-col-filters');
    var delete_btn = $(table).attr('data-delete');

    var job_id = $(table_elem).attr('data-job-id');
    var update_url = '/developer/gizmos/ajax/' + job_id + '/update-row';
    $.ajax({
        method: 'POST',
        url: update_url,
        data: {results_url: results_url, run: run, filters: filters, status: status, actions: actions, delete: delete_btn}
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
                }, 4000);
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
    //update_status(this);
});

$('.job-row').each(function(){
   update_row(this);
});