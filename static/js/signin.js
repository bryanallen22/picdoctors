// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

  $('input:radio[name=createAcctRadio]').click( function() {
    var checked = $(this).val();
    if( checked == "create" ) {
      // Creating an account
      $("#confirmPassword").show();
    }
    else if( checked == "have" ) {
      // They already have an account
      $("#confirmPassword").hide();
    }
  });

});
