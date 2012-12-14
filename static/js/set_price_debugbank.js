
// This file prepopulates some bank acct info in debug mode for testing.
// It should never make it to production (but even so, it's not a security
// risk since these won't actually work in production).

// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

  $("#btn-badrouting").click( function() {
    $("input.ba-name").val( 'Mr. Invalid Routing Number' );
    $("input.ba-rn").val( '100000007' );
    $("input.ba-an").val( '8887776665555' );
    $("select option[value='checking']").attr('selected', 'selected');
  });

  $("#btn-pending").click( function() {
    $("input.ba-name").val( 'Mr State Goes to Pending' );
    $("input.ba-rn").val( '021000021' );
    $("input.ba-an").val( '9900000000' );
    $("select option[value='checking']").attr('selected', 'selected');
  });

  $("#btn-paid").click( function() {
    $("input.ba-name").val( 'Mr. state goes to paid' );
    $("input.ba-rn").val( '021000021' );
    $("input.ba-an").val( '9900000002' );
    $("select option[value='checking']").attr('selected', 'selected');
  });

  $("#btn-failed").click( function() {
    $("input.ba-name").val( 'Mr. state goes to failed' );
    $("input.ba-rn").val( '021000021' );
    $("input.ba-an").val( '9900000004' );
    $("select option[value='checking']").attr('selected', 'selected');
  });

});
