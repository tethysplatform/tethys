// Check if Internet Explorer
(function check_ie() {
    var ua = window.navigator.userAgent;
    var msie = ua.indexOf("MSIE ");
    var error_message = "This app does not support Internet Explorer. Please switch to another browser."
    if (msie > 0)  // IE 10 or less
    {
        alert(error_message)
    }
    else {
        var trident = ua.indexOf('Trident/');
        if (trident > 0) { // IE 11
            alert(error_message)
        }
    }
})()