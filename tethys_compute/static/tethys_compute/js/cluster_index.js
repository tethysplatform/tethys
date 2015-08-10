/*****************************************************************************
 * FILE: cluster_index.js
 * DATE: 2015
 * AUTHOR: Scott Christense
 * COPYRIGHT: (c) Brigham Young University 2015
 * LICENSE: BSD 2-Clause
 *****************************************************************************/
function add_listeners(ref_elem, update_elem, update_btn){
    function update(){
        update_elem.value = ref_elem.value;
        update_btn.removeAttribute('disabled');
    }
    ref_elem.addEventListener('mousedown', function(){
        this.addEventListener('mousemove', update);
    });
    ref_elem.addEventListener('mouseup', function(){
        this.removeEventListener('mousemove', update)
        update();
    });
}

var size_output_elems = document.getElementsByName('size_output');
for(var i=0, len=size_output_elems.length;i<len;i++){
    var size_output_elem = size_output_elems[i];
    var size_id = size_output_elem.getAttribute('for');
    var size_elem = document.getElementById(size_id);
    var btn_id = size_output_elem.getAttribute('btn_id');
    var update_btn = document.getElementById(btn_id);
    add_listeners(size_elem, size_output_elem, update_btn);
}

document.getElementById('create_form').addEventListener('submit',function(){
    document.getElementById('create_submit').hidden = true;
    document.getElementById('size').setAttribute('readonly','true');
    document.getElementById('name').setAttribute('readonly', 'true');
    document.getElementById('loader').hidden = false;
});

document.getElementById('create_link').addEventListener('click', function(event){
    document.getElementById('create_row').hidden = false;
    event.preventDefault();
}, false);