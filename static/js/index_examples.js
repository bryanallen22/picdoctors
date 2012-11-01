// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

  var cur_row = 0;
  var delay = 8000;

  var toggleNext = function() {
    var example_rows = $(".examplerow");

    var next_row = cur_row + 1;
    if( next_row >= example_rows.length ) {
      next_row = 0;
    }

    $(example_rows[cur_row]).fadeOut( function() {
      $(example_rows[next_row]).fadeIn( function() {
        cur_row = next_row;
        window.setTimeout( toggleNext, delay );
      });
    });

  }

  window.setTimeout( toggleNext, delay );


});
