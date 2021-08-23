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

  var betamodalform = "<form action='/apps/send-beta-feedback/' method='post' enctype='multipart/form-data' id='uploadBetaFeedback' name='uploadBetaFeedback'>"+
                        "<div class='betaForm'>"+
                          "<div>"+
                            "<h4>Feedback</h4>"+
                          "</div>"+
                          "<div>"+
                            "<label>Username</label>"+
                            "<p>"+username+"</p>"+
                          "</div>"+
                          "<div style='width:320px; padding-bottom:15px; padding-right:5%'>"+
                            "<label for='betaUserComments'>Comments</label>"+
                            "<textarea form='uploadBetaFeedback' id='betaUserComments' name='betaUserComments' style='width:100%; resize: none;' rows='9'></textarea>"+
                          "</div>"+
                          "<div id='hidden-fields'>"+
                            "<input type='hidden' form='uploadBetaFeedback' name='betaUser' id='betaUser' value="+username+">"+
                            "<input type='hidden' form='uploadBetaFeedback' name='betaSubmitLocalTime' id='betaSubmitLocalTime' value='"+local_date_time+"'>"+
                            "<input type='hidden' form='uploadBetaFeedback' name='betaSubmitUTCOffset' id='betaSubmitUTCOffset' value="+utc_offset_in_hours+">"+
                            "<input type='hidden' form='uploadBetaFeedback' name='betaFormUrl' id='betaFormUrl' value="+window.location.href+">"+
                            "<textarea form='uploadBetaFeedback' name='betaFormUserAgent' id='betaFormUserAgent' style='display: none;'>"+navigator.userAgent+"</textarea>"+
                            "<textarea form='uploadBetaFeedback' name='betaFormVendor' id='betaFormVendor' style='display: none;'>"+navigator.vendor+"</textarea>"+
                          "</div>"+
                          "<input type='hidden' name='csrfmiddlewaretoken' value="+csrftoken+">"+
                          "<div style='width:100%'>"+
                            "<button id='cancelBetaForm' class='btn btn-default' type='button'>Cancel</button>"+
                            "<button id='submitBetaForm'  class='btn btn-default' type='button'>Submit</button>"+
                          "</div>"+
                        "</div>"+
                      "</form>";

    var betamodalformSuccess = "<div class='betaFormSuccess' id='betamodalformSuccess'>"+
                                 "<h6>Thank you for your feedback!<h6>"+
                               "</div>";

    var betamodalformError = "<div class='betaFormError' id='betamodalformError'>"+
                               "<h6>We're sorry, but your feedback has not been received due to an error. "+
                               "Please, try again later.</h6>"+
                             "</div>";

  $("body").append('<button id="beta-feedback-button">Feedback</button>');

  //Make the feedback form on click of the feedback button
  $("#beta-feedback-button").on("click", function() {
    $("body").append('<div id="darkBackground"></div>');
    $("body").append('<div id="beta-feedback-modal-wrapper"><div id="beta-feedback-modal"></div></div>');
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

            setTimeout(function () {
              $("#beta-feedback-modal-wrapper").remove();
              $("#darkBackground").remove();
            }, 2000);
          },
          error: function(data) {
            $("#uploadBetaFeedback").remove();
            $("#beta-feedback-modal").append(betamodalformError);

            setTimeout(function () {
              $("#beta-feedback-modal-wrapper").remove();
              $("#darkBackground").remove();
            }, 4000);
          }
        });
    });

    $("#cancelBetaForm").on("click", function() {
        $("#darkBackground").remove();
        $("#beta-feedback-modal-wrapper").remove();
    });
  });
});




