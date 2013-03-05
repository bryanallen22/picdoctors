// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

  $('#myCarousel').carousel({
      interval: 8000,
      pause: null, /* Don't pause when they hover over it */

  });

  $('.hero-unit').mouseenter( function() {
    $('#myCarousel').carousel( 'pause' );
  });

  $('.hero-unit').mouseleave( function() {
    /* So, this is annoying. Doing this resets the time, so if you
     * briefly hover on the picture it makes that cycle seem a lot
     * longer. Unfortunately, there's no better way exposed unless
     * I want to modify bootstrap itself. Which I don't want to now. */
    $('#myCarousel').carousel( 'cycle' );
  });

});
