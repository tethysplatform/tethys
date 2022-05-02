/*****************************************************************************
 * FILE:    collapse-element.js
 * DATE:    October 24, 2018
 * AUTHOR:  Nathan Swain
 * COPYRIGHT: (c) Aquaveo 2018
 * LICENSE:
 *****************************************************************************/
// Credits: https://css-tricks.com/using-css-transitions-auto-dimensions/

function collapse_section(element) {
  // get the height of the element's inner content, regardless of its actual size
  var section_height = element.scrollHeight;
  
  // temporarily disable all css transitions
  var element_transistion = element.style.transition;
  element.style.transition = '';
  
  // on the next frame (as soon as the previous style change has taken effect),
  // explicitly set the element's height to its current pixel height, so we 
  // aren't transitioning out of 'auto'
  requestAnimationFrame(function() {
    element.style.height = section_height + 'px';
    element.style.overflow = 'hidden';
    element.style.transition = element_transistion;
    
    // on the next frame (as soon as the previous style change has taken effect),
    // have the element transition to height: 0
    requestAnimationFrame(function() {
      element.style.height = 0 + 'px';
    });
  });
  
  // mark the section as "currently collapsed"
  element.setAttribute('data-collapsed', 'true');
}

function expand_section(element) {
  // get the height of the element's inner content, regardless of its actual size
  var section_height = element.scrollHeight;
  
  // have the element transition to the height of its inner content
  element.style.height = section_height + 'px';

  // when the next css transition finishes (which should be the one we just triggered)
  element.addEventListener('transitionend', function(e) {
    // remove this event listener so it only gets triggered once
    element.removeEventListener('transitionend', arguments.callee);
    
    // remove "height" from the element's inline styles, so it can return to its initial value
    element.style.height = null;
    element.style.overflow = 'unset';
  });
  
  // mark the section as "currently not collapsed"
  element.setAttribute('data-collapsed', 'false');
}