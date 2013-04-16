// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

  var animate_markup = function() {
    var example_markup = $("#example_markup");
    //
    // Reset to defaults (if you change these, be sure to change it in picdoctors.less
    example_markup.css( { "width" : "40px", "height" : "40px" } );
    example_markup.show()

    example_markup.delay(1000).animate( { "width" : 175, "height" : 120 } )
  }

  // Call it immediately
  animate_markup();
  // and then call it every 4 seconds
  setInterval(animate_markup, 4000);

});
