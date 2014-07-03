// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

  if( $('#setprice_app').length > 0 ) {

    var CSRF_TOKEN = $('input[name=csrfmiddlewaretoken]').attr('value');

    /*
     * Once we get a 1 time token from stripe, we get here
     */
    function stripeResponseHandler(status, response) {
      var $form = $('#payment-form');

      if (response.error) {
        // Show the errors on the form
        $form.find('.payment-errors').text(response.error.message);
        $form.find('button').prop('disabled', false);
      } else {
        // response contains id and card, which contains additional card details
        var token = response.id;
        // Insert the token into the form so it gets submitted to the server
        $form.append($('<input type="hidden" name="stripeToken" />').val(token));
        // and submit
        $form.get(0).submit();
      }
    };

    $('#payment-form').submit(function(event) {
      var $form = $(this);

      // Disable the submit button to prevent repeated clicks
      $form.find('button').prop('disabled', true);

      var checked = $(".radio:checked")
      if( checked.val() == "new_card" ) {
        Stripe.card.createToken($form, stripeResponseHandler);
      }
      else {
        var card_id = checked.parent().find('.id').html();
        $form.get(0).submit();
      }

      // Prevent the form from submitting with the default action
      return false;
    });

    /*******************************************/
    /*******************************************/
    /*******************************************/

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

