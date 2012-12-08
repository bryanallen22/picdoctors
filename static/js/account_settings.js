// This script gets loaded on both the account settings page for both users
// and doctors.

// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

  /* .user_card doesn't exist on doctor settings pages, but that's okay */
  $('.user_card button').click( function(e) {
    e.preventDefault();

    // Prevent them from clicking again
    $(this).attr('disabled', 'disabled');

    var CSRF_TOKEN = $('input[name=csrfmiddlewaretoken]').attr('value');
    var card_div = $(this).closest('.user_card');
    var card_uri = card_div.find('.uri').text();
    var obj = { "card_uri" : card_uri };

    $.ajax({
      headers: {
        "X-CSRFToken":CSRF_TOKEN
      },
      type: "POST",
      url: '/account_settings_delete_card/',
      data: obj,
      success : function(data, textStatus) {
        if ( data.success ) {
          card_div.remove();
        }
        else {
          // Silently fail to do anything if we are unable to delete.
          // REVISIT

          // I suppose we can at least let them try again?
          $(this).removeAttr('disabled');
        }
      },
    });
  });

});

