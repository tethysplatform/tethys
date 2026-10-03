function get_csrf_token() {
    var csrfValue = null;
    var name = 'csrftoken';
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                csrfValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    if (csrfValue === null) {
        var input = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (input) {
            csrfValue = input.value;
        }
    }
    return csrfValue;
}