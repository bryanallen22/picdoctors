// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

  function stripeResponseHandler(status, response) {
      if (response.error) {
          // show the errors on the form
          $("#payment-errors").text(response.error.message).show();
          $(".submit-button").removeAttr("disabled");
      } else {
          var form$ = $("#payment-form");
          // token contains id, last4, and card type
          var token = response['id'];
          // insert the token into the form so it gets submitted to the server
          form$.append("<input type='hidden' name='stripeToken' value='" 
                        + token + "'/>");
          // and submit
          form$.get(0).submit();
      }
  }

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
      $("#price").val( '$' + (priceDbl).toMoney(2, '.', ',') );
    }
  } );

  $(document).ready(function() {
    $("#payment-form").submit(function(event) {
      // disable the submit button to prevent repeated clicks
      $('.submit-button').attr("disabled", "disabled");

      Stripe.createToken({
          number: $('.card-number').val(),
          cvc: $('.card-cvc').val(),
          exp_month: $('.card-expiry-month').val(),
          exp_year: $('.card-expiry-year').val()
      }, stripeResponseHandler);

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

});

