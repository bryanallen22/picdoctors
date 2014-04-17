// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

  if( $('#setprice_app').length > 0 ) {
    balanced.init(marketplace_uri);
    var CSRF_TOKEN = $('input[name=csrfmiddlewaretoken]').attr('value');

    var debug = function (tag, content) {
      //$('<' + tag + '>' + content + '</' + tag + '>').appendTo('#result');
      //$('<br/><br/>').appendTo('#result');
    };

    var createHold = function(card_uri, price)
    {
      var obj = { "card_uri" : card_uri, 'price' : price };

      $.ajax({
        headers: {
          "X-CSRFToken":CSRF_TOKEN
        },
        type: "POST",
        url: '/create_hold_handler/',
        data: obj,
        success : function(data, textStatus) {
          if ( data.status == '402' ) {
            $('#min-price-msg').show();
            $('.submit-button').removeAttr("disabled");
          }
          else if ( data.status == '200' ) {
            // Okay, payment accepted, let's move off this page
            document.location.href = data.next;
          }
        },
      });
    }

    var balancedCallback = function(response) {
      // response.data - An object containing the URI of the newly created account.
      // response.error - Details of the error.
      // response.status - HTTP response code.
      var tag = (response.status < 300) ? 'pre' : 'code';
      debug(tag, JSON.stringify(response));

      switch (response.status) {
        case 400:
          // missing field - check response.error for details


          $('.submit-button').removeAttr("disabled");

          var gotError = false;

          // White list a few errors here
          if( response.error.card_number ) {
            $("#error_card").show();
            gotError = true;
          }
          if( response.error.expiration ) {
            $("#error_exp").show();
            gotError = true;
          }
          if( response.error.security_code ) {
            $("#error_seccode").show();
            gotError = true;
          }

          if( !gotError ) {
            // We've got some kind of 400 error, but we don't have
            // it whitelisted. Still show some generic error
            $("#error_400").show();
          }

          break;
        case 402:
          // we couldn't authorize the buyer's credit card
          // check response.error for details
          $('.submit-button').removeAttr("disabled");
          $("#error_402").show();
          break
        case 404:
          // your marketplace URI is incorrect
          $('.submit-button').removeAttr("disabled");
          $("#error_404").show();
          break;
        case 201:
          // WOO HOO!
          // response.data.uri == uri of the card or bank account resource

          // Add 'price' to our post data
          var price = $('#price').val();
          var card_uri = response.data.uri;
          createHold(card_uri, price);
      }
    }

    var tokenizeCard = function() {
      var $form = $('form#payment');
      var cardData = {
        // strip out '-' and ' ' from credit card
        card_number: $form.find('[name="card_number"]').val().replace(/[- ]/g, ''),
        expiration_month: $form.find('[name="expiration_month"]').val(),
        expiration_year: $form.find('[name="expiration_year"]').val(),
        security_code: $form.find('[name="security_code"]').val()
      };

      balanced.card.create(cardData, balancedCallback);
    };

    $('#payment').submit( function(e) {

      e.preventDefault();
      $('.submit-button').attr("disabled", "disabled");

      // Hide all errors. They'll come back server side if they are valid
      $(".balanced_error").hide();

      // If there is a checked radio button exists for an existing credit card,
      // we need to use that one.
      var checked = $('input.radio.existing:checked');
      if ( checked.length > 0 )
      {
        var card_uri = checked.parent().find(".uri").text();
        var price = $('#price').val();
        createHold(card_uri, price);
      }
      else
      {
        tokenizeCard();
      }
    } );

    /*******************************************/
    /*******************************************/
    /*******************************************/

    $(".new_card input").focus( function() {
      $(this).closest('.card_choice').find(".radio").attr('checked', true);
    });

    $("input[name='expiration_year']").change( function() {
      var val = $(this).val();
      if( parseInt(val) < 100 ) {
        // They're just putting the last two digits. Go ahead
        // and add in the first two.
        // Note to Y2.1K programmers: Change this!
        $(this).val('20' + val);
      }
    });

    $("#new_card_radio").click( function() {
      if ($(this).is(':checked'))
      {
        $(".newcc_collapsible").show();
      }
    });

    $("#price").focusout( function() {
      /* minimum_price is set directly in the html page above this script */
      if( parseFloat($("#price").val()) < minimum_price ) {
        $("#min-price-msg").show();
        $('.submit-button').attr("disabled", "disabled");
      }
      else {
        $("#min-price-msg").hide();
        $('.submit-button').removeAttr("disabled");
      }

      var priceStr = $("#price").val();
      var priceDbl = parseFloat(priceStr);
      if( priceDbl ) {
        $("#price").val( (priceDbl).toMoney(2, '.', ',') );
      }
    } );

    $(document).ready(function() {
      $("#payment-form").submit(function(event) {
        // disable the submit button to prevent repeated clicks
        $('.submit-button').attr("disabled", "disabled");

        // prevent the form from submitting with the default action
        return false;
      });
    });

    /*
     * This magic method is a copy paste from here:
     *
     * http://stackoverflow.com/questions/149055/how-can-i-format-numbers-as-money-in-javascript
     *
     * decimal_sep: character used as decimal separtor, it defaults to '.' when omitted
     * thousands_sep: char used as thousands separator, it defaults to ',' when omitted
     */
    Number.prototype.toMoney = function(decimals, decimal_sep, thousands_sep)
    {
      var n = this,
          // How many decimals to show
          c = isNaN(decimals) ? 2 : Math.abs(decimals),
          // decimal separator defaults to '.'
          d = decimal_sep || '.',

          // pass "" to not use thousands separator
          t = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,

          sign = (n < 0) ? '-' : '',

          //extracting the absolute value of the integer part of the number and converting to string
          i = parseInt(n = Math.abs(n).toFixed(c)) + '',

          j = ((j = i.length) > 3) ? j % 3 : 0;

      return sign + (j ? i.substr(0, j) + t : '')
        + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t)
        + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : '');
    }

  }
});

