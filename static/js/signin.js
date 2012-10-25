// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

  /* If the radio button says they've got an account, hide the confirm password
   * button. This shouldn't normally be necessary, but if they hit the back button
   * or something it can be checked. */
  if( $('input:radio[name=create_acct_radio]:checked').val() == 'have' ) {
      $("#confirm_password").hide();
      $("#tos").hide();
  }

  $('input:radio[name=create_acct_radio]').click( function() {
    var checked = $(this).val();
    if( checked == "create" ) {
      // Creating an account
      $("#confirm_password").show();
      $("#tos").show();
    }
    else if( checked == "have" ) {
      // They already have an account
      $("#confirm_password").hide();
      $("#tos").hide();
    }
  });

});
