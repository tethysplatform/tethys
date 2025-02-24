'use strict';
(function () {
    var DISCONNECTED = false;
    var MAX_WAIT = 180000;
    var CURRENT_WAIT = 0;
    var ITER_WAIT = 2000;
    var INTERVAL = window.setInterval(() => {
        CURRENT_WAIT += ITER_WAIT;
        if (CURRENT_WAIT > MAX_WAIT) {
            window.clearInterval(INTERVAL);
        }
        $.get('/')
            .then(data => { 
                if (DISCONNECTED) {
                    window.location = REDIRECT_URL;
                }
            })
            .catch(err => DISCONNECTED = true)
    }, ITER_WAIT)
}())