/*****************************************************************************
 * FILE:      gizmo_utilities.js
 * DATE:      9 October 2015
 * AUTHOR:    Nathan Swain
 * COPYRIGHT: (c) Brigham Young University 2015
 * LICENSE:   BSD 2-Clause
 *****************************************************************************/
// add function changeSize to jQuery prototype
// this is used for the map view but available for all jQuery elements
$.fn.changeSize = function(fn){
    var $this = this,
    w0 = $this.width(),
    h0 = $this.height(),
    pause = false,
    callback,                       //callback function after handle is called
    handler;                        //function to handle action

    callback = function(){
      pause = false;
      w0 = $this.width();
      h0 = $this.height();
    }
    handler = function(){
      fn($this);
      callback();
    }

    $this.sizeTO = setInterval(function(){
        if (!pause){
            var w1 = $this.width();
            var h1 = $this.height();
            if (w1 != w0 || h1 != h0) {
                pause = true;
                handler();
            }
        }
    }, 100);
};