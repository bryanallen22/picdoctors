// This file prepopulates some card info in debug mode for testing.
// It should never make it to production (but even so, it's not a security
// risk since these won't actually work in production).

// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

  $("#btn-visa").click( function() {
    $("#cc_num").val( '4242424242424242' );
    $("#cvc").val( '123' );
    $("#cc_month").val( '04' );
    $("#cc_year").val( '2016' );
  });

  $("#btn-amex").click( function() {
    $("#cc_num").val( '4242424242424242' );
    $("#cvc").val( '1234' );
    $("#cc_month").val( '06' );
    $("#cc_year").val( '2016' );
  });

  $("#btn-mastercard").click( function() {
    $("#cc_num").val( '4242424242424242' );
    $("#cvc").val( '123' );
    $("#cc_month").val( '09' );
    $("#cc_year").val( '2016' );
  });

});
