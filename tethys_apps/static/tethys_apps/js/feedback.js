// Convert a UTC timestamp in milliseconds to a readable format
function getDateandTime(){
  var a = new Date();
  var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  var year = a.getFullYear();
  var month = months[a.getMonth()];
  var date = a.getDate();
  var hour = a.getHours();
  var min = a.getMinutes();
  var sec = a.getSeconds();
  var time = date + ' ' + month + ' ' + year + ' ' + hour + ':' + min + ':' + sec ;
  return time;
}


$(document).ready(function(){
  // Note that UTC offset means that the offset is positive if the local timezone is behind UTC and negative if it is ahead.
  // MST is 7 hours behind UTC
  var utc_offset_in_hours = new Date().getTimezoneOffset()/60;
  var local_date_time = getDateandTime();
  var username = document.getElementById('page-attributes').getAttribute('data-username');

  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }

  // using jQuery
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
  console.log(csrftoken);

  var betamodalform = "<form action='/apps/send-beta-feedback/' method='post' enctype='multipart/form-data' id='uploadBetaFeedback' name='uploadBetaFeedback'>"+
                            "<div class='betaForm'>"+
                            "<div>"+
                                "<h4>Feedback</h4>"+
                            "</div>"+
                            "<div>"+
                                "<h6>Username</h6>"+
                                "<input type='hidden' form='uploadBetaFeedback' name='betaUser' id='betaUser' value="+username+">"+username+
                            "</div>"+
                            "<div style='width: 350px'>"+
                                "<h6>Time</h6>"+
                                "<input type='hidden' form='uploadBetaFeedback' name='betaSubmitLocalTime' id='betaSubmitLocalTime' value='"+local_date_time+"'>"+
                                "<input type='hidden' form='uploadBetaFeedback' name='betaSubmitUTCOffset' id='betaSubmitUTCOffset' value="+utc_offset_in_hours+">"+
                                local_date_time+" with UTC-offset of "+utc_offset_in_hours+" hours"+
                            "</div>"+
                            "<div style='width: 300px; height: 90px; overflow: hidden;'>"+
                                "<h6>URL</h6>"+
                                "<input type='hidden' form='uploadBetaFeedback' name='betaFormUrl' id='betaFormUrl' value="+window.location.href+">"+window.location.href+"<br>"+
                            "</div>"+
                            "<div style='width:320px; padding-bottom:15px; padding-right:5%'>"+
                                "<h6>Comments</h6>"+
                                    "<textarea form='uploadBetaFeedback' id='betaUserComments' name='betaUserComments' style='width:100%; resize:none;' rows=9></textarea>"+
                            "</div>"+
                            "<input type='hidden' name='csrfmiddlewaretoken' value="+csrftoken+">"+
                            "<div style='width:100%'>"+
                            "<button id='cancelBetaForm' type='button'>Cancel</button>&nbsp;&nbsp<button id='submitBetaForm' type='button'>Submit</button>"+
                            "</div>"+
                          "</div>"+
                          "</form>";

    var betamodalformSuccess = "<div class='betaFormSuccess' id='betamodalformSuccess'>"+
                            "<h6>Thank you for your feedback!<h6>"+
                            "</div>";

    var betamodalformError = "<div class='betaFormError' id='betamodalformError'>"+
                            "<h6>Feedback Not Submitted Due To Error</h6>"+
                            "<h6>Please Contact App Admin</h6>"+
                            "</div>";

  $("body").append('<button id="beta-feedback-button">Feedback</button>');

//Make the feedback form on click of the feedback button
  $("#beta-feedback-button").on("click", function() {
    console.log(local_date_time);
    $("body").append('<div id="darkBackground"></div>');
    $("body").append('<div  id="beta-feedback-modal"></div>');
    $("#beta-feedback-modal").append(betamodalform);


   //Using Ajax, validate the form, submit, and redirect to home page
    $("#submitBetaForm").on("click", function() {
       var formdata = $('#uploadBetaFeedback').serializeArray();
       $.ajax({
          url: '/apps/send-beta-feedback/',
          type: 'POST',
          data: formdata,
          success: function(data) {
                $("#uploadBetaFeedback").remove();
                $("#beta-feedback-modal").append(betamodalformSuccess);
                setTimeout(function () {$("#beta-feedback-modal").remove();$("#darkBackground").remove(); }, 2000);

          },
          error: function(data) {
                $("#uploadBetaFeedback").remove();
                $("#beta-feedback-modal").append(betamodalformError);
                setTimeout(function () {$("#beta-feedback-modal").remove();$("#darkBackground").remove(); }, 3000);
          }
        });
    });

    $("#cancelBetaForm").on("click", function() {
        $("#darkBackground").remove();
        $("#beta-feedback-modal").remove();
    });
  });
});




