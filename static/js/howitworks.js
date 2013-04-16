// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

  var example_markup = $("#example_markup");
  var init_example_width  = example_markup.css("width");
  var init_example_height = example_markup.css("height");
  var animate_markup = function() {
    example_markup.css( { "width" : init_example_width, "height" : init_example_height } );
    example_markup.delay(1000).animate( { "width" : 175, "height" : 120 } )
  }

  // Call it immediately
  animate_markup();
  // and then call it every 4 seconds
  setInterval(animate_markup, 4000);

});
