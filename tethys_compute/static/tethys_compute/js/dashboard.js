var elementisClicked = false;

function clickHandler() {
    elementisClicked = true;
    window.location.href = '';
}

function count_hyphen(string) {
    return (string.match(/-/g) || []).length
}

for(var els = document.getElementsByTagName('div'), i = els.length; i--;){
    // bokeh id has 4 hyphen on status page
    if ((els[i].id.length == 36 && count_hyphen(els[i].id) == 4) || els[i].id == 'graph' || els[i].id == 'task_stream') {
        console.log(els[i].id + ' hyphen: ' + count_hyphen(els[i].id))
        els[i].addEventListener("click", clickHandler)
    }
    else{}
}
