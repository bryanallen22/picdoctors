// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

  $('input:radio[name=create_acct_radio]').click( function() {
    var checked = $(this).val();
    if( checked == "create" ) {
      // Creating an account
      $("#confirm_password").show();
    }
    else if( checked == "have" ) {
      // They already have an account
      $("#confirm_password").hide();
    }
  });

});
