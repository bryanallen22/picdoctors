// This script gets loaded on both the account settings page for both users
// and doctors.

// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){
  /* .user_card doesn't exist on doctor settings pages, but that's okay */
  /* Removed -- for now, we're just processing the cards as part of the normal checkout flow
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
  */

  /* uri comes directly from template */
  balanced.init(marketplace_uri);

  var $form = $('#bank-account-form');

  function callbackHandler(response) {
    switch (response.status) {
      case 201:
        // WOO HOO!
        // response.data.uri == uri of the card or bank account resource
        break;
      case 400:
        // missing field - check response.error for details
        break;
      case 402:
        // we couldn't authorize the buyer's credit card
        // check response.error for details
        break
      case 404:
        // your marketplace URI is incorrect
        break;
      case 500:
        // Balanced did something bad, please retry the request
        break;
    }
  }

  var createAcct = function() {
    var bankAccountData = {
       "name": $form.find(".ba-name").val(),
       "account_number": $form.find(".ba-an").val(),
       "routing_number": $form.find(".ba-rn").val(),
       "type": $form.find("select option:selected").val(),
    }

    debugger

    if( !balanced.bankAccount.validateRoutingNumber( bankAccountData.routing_number) )
    {
      $("#routing-error").show();
      return;
    }

    if( !balanced.bankAccount.validate({
           'routing_number' : bankAccountData.routing_number,
           'account_number' : bankAccountData.account_number,
           'jk' : bankAccountData.name }))
    {
      debugger
    }

    debugger

    balanced.bankAccount.create(bankAccountData, callbackHandler);
  }

  $form.find("button:submit").click( function(e) {
    e.preventDefault();
    createAcct();
  });

});

