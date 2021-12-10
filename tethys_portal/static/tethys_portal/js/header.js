// Sticky header
document.addEventListener("DOMContentLoaded", function(){
  window.addEventListener('scroll', function() {
      if (window.scrollY > 16) {
        document.getElementById('header-navbar').classList.add('fixed-top');
        document.getElementById('header-navbar').classList.remove('mx-5');
        // add padding top to clear-header element
        let navbar_height = document.querySelector('#header-navbar').offsetHeight;
        document.querySelector('.clear-header').style.paddingTop = navbar_height + 'px';
      } else {
        document.getElementById('header-navbar').classList.remove('fixed-top');
        document.getElementById('header-navbar').classList.add('mx-5');
        // remove padding top from clear-header element
        document.querySelector('.clear-header').style.paddingTop = 0;
      } 
  });
}); 