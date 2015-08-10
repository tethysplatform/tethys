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

function update_status(table_elem){
    var job_id = $(table_elem).attr('data-job-id');
    var results_url = $(table_elem).attr('data-results-url');
    var run = $(table_elem).attr('data-run');
    var filters = $(table_elem).parent().parent().parent().attr('data-col-filters');
    console.log(filters);
    var update_url = '/developer/gizmos/ajax/' + job_id + '/update-status';
    $.ajax({
        method: 'POST',
        url: update_url,
        data: {results_url: results_url, run: run}
    }).done(function(json){
        if(json.success){
            $(table_elem).html(json.html);
            status = json.status;
            if(status == 'Running' || status == 'Submitted' || status == 'Various'){
                setTimeout(function(){
                    update_status(table_elem);
                }, 4000);
            }
        }
    });
}

$('.btn-job-run').each(function(){
    var job_id = $(this).attr('data-job-id');
    $(this).on('click', function(){
       var execute_url = '/developer/gizmos/ajax/' + job_id + '/execute';
       $.ajax({
          url: execute_url
       }).done(function(json){
           update_status($('#jobs-table-status-' + job_id));
       });
    });
});

$('.btn-job-delete').each(function(){
    var job_id = $(this).attr('data-job-id');
    $(this).on('click', function(){
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
});

$('.job-status').each(function(){
    update_status(this);
});