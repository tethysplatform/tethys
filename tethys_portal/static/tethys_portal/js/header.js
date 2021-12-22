// Sticky header
document.addEventListener("DOMContentLoaded", function(){
  window.addEventListener('scroll', function() {
      let viewport_height = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);
      let body_height = document.querySelector('body').scrollHeight;
      let navbar_height = document.querySelector('#header-navbar').offsetHeight;
      scrollable_height = body_height - viewport_height;

      // Only change the header to fixed if it can be cleared by the height available to scroll
      // Prevents a bug that will cause the header to flash back and forth between fixed and not 
      // fixed, preventing scrolling
      if (scrollable_height > navbar_height) {
        if (window.scrollY > 16) {
          document.getElementById('header-navbar').classList.add('fixed-top');
          document.getElementById('header-navbar').classList.remove('mx-5');
          // add padding top to clear-header element
          document.querySelector('.clear-header').style.paddingTop = navbar_height + 'px';
        } else {
          document.getElementById('header-navbar').classList.remove('fixed-top');
          document.getElementById('header-navbar').classList.add('mx-5');
          // remove padding top from clear-header element
          document.querySelector('.clear-header').style.paddingTop = 0;
        }
      }
  });
}); 