// This script gets loaded on both the account settings page for both users
// and doctors.

// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){
  /* uri comes directly from template */
  balanced.init(marketplace_uri);

  var $form = $('#bank-account-form');

  function submitToken(bank_account_uri) {
    var CSRF_TOKEN = $('input[name=csrfmiddlewaretoken]').attr('value');

    var obj = { "bank_account_uri" : bank_account_uri };

    $.ajax({
      headers: {
        "X-CSRFToken":CSRF_TOKEN
      },
      type: "POST",
      url: '/create_bank_account/',
      data: obj,
      success : function(data, textStatus) {
          debugger
        if ( data.success ) {
          // reload page?
        }
        else {
          // Silently fail to do anything if we are unable to delete.
          // REVISIT
        }
      },
    });

  }

  function callbackHandler(response) {
    switch (response.status) {
      case 201:
        // WOO HOO!
        // response.data.uri == uri of the card or bank account resource
        submitToken(response.data.uri);
        break;

      case 400:
        // missing field - check response.error for details
        //break;
      case 402:
        // we couldn't authorize the buyer's credit card
        // check response.error for details
        //break;
      case 404:
        // your marketplace URI is incorrect
        //break;
      case 500:
        // Balanced did something bad, please retry the request
        //break;
      default:
        $('#error_bankaccount').show();
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

    if( !balanced.bankAccount.validateRoutingNumber( bankAccountData.routing_number) )
    {
      $("#routing-error").show();
      return;
    }

    if( !balanced.bankAccount.validate({
           'routing_number' : bankAccountData.routing_number,
           'account_number' : bankAccountData.account_number,
           'name'           : bankAccountData.name }))
    {
      $('#error_bankaccount').show();
    }

    balanced.bankAccount.create(bankAccountData, callbackHandler);
  }

  $form.find("button:submit").click( function(e) {
    e.preventDefault();
    $('#error_bankaccount').hide();
    createAcct();
  });

});

