// This file prepopulates some card info in debug mode for testing.
// It should never make it to production (but even so, it's not a security
// risk since these won't actually work in production).

// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

  $("#btn-visa").click( function() {
    $("input[name='card_number']").val( '4111111111111111' );
    $("input[name='security_code']").val( '123' );
    $("input[name='expiration_month']").val( '04' );
    $("input[name='expiration_year']").val( '2014' );
  });

  $("#btn-amex").click( function() {
    $("input[name='card_number']").val( '341111111111111' );
    $("input[name='security_code']").val( '1234' );
    $("input[name='expiration_month']").val( '06' );
    $("input[name='expiration_year']").val( '2015' );
  });

  $("#btn-mastercard").click( function() {
    $("input[name='card_number']").val( '5105105105105100' );
    $("input[name='security_code']").val( '123' );
    $("input[name='expiration_month']").val( '09' );
    $("input[name='expiration_year']").val( '2016' );
  });

});
