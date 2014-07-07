
/*
 * Everybody wants this postTo thing, so I'm adding it globally. Don't sue me, I
 * think it actually is appropriate.
 */
function postTo(url, obj, callback, errorCallback) {
  var CSRF_TOKEN = $('input[name=csrfmiddlewaretoken]').attr('value');
  $.ajax({
    headers: {
      "X-CSRFToken":CSRF_TOKEN
    },
    type: "POST",
    url: url,
    data: obj,
    success : callback,
    error : errorCallback
  });

}

/*
 * Feedback stuff
 */
$(function(){

  var user_feedback = "";
  var from_feedback = "";
  //for use if they start to add feedback again while we are showing off our thank you
  var current_popup_state = 1;

  var users_entered_data = true;

  $("#feedback_link").click( function(e) {
    // stop it from navigating
    e.preventDefault();

    current_popup_state += 1;

    //console.log('feedback');
    var el = $(this);
    var data_set = el.attr('data-set');
    data_set = Boolean(data_set); //anything that isn't blank is true to me!


    var cur_input = $('#feedback_textarea');
    var cur_from = $('#feedback_from_textarea');
    if(cur_input.length > 0){
      user_feedback = $.trim(cur_input.val());
      from_feedback = $.trim(cur_from.val());
      //console.log('setting feedback');
    }else{
      if(user_feedback!= ''){
        setTimeout('fill_previous_feedback()', 20);
      }
    }

    if(!data_set){
      el.popover({ html : true });
      var template = $('#feedback_form').html().trim();
      el.attr('data-set', users_entered_data);
      el.attr('data-content', template);
      el.attr('data-original-title','We appreciate your feedback!');
    }
    el.popover('toggle');
  });

  $(".feedback_submit").on('click', function() {
    //console.log('submit_feedback');
    var cur_input = $('#feedback_textarea');
    var cur_from = $('#feedback_from_textarea');
    if(cur_input.length > 0){
      var el = $('#feedback_link');
      el.popover('hide');

      user_feedback = $.trim(cur_input.val());
      from_feedback = $.trim(cur_from.val());
      var CSRF_TOKEN = $('input[name=csrfmiddlewaretoken]').attr('value');

      var json_data = JSON.stringify(
        {
          "from_whom" : from_feedback,
          "user_feedback" : user_feedback,
        }
      );
        
      current_popup_state += 1;
      var popup_state_when_posted = current_popup_state;
      $.ajax({
        headers: {
          "X-CSRFToken":CSRF_TOKEN
        },
        type: 'POST',
        url:  '/feedback/' ,
        data: json_data,
        success : function(data, textStatus) {
          //console.log(data);
          //console.log(textStatus);
          if(data.success){
            show_result('feedback_thanks', 'Feedback Submitted', popup_state_when_posted);
          } else {
            show_result('feedback_thanks_but', 'Feedback Not Submitted', popup_state_when_posted);
          }
        },
      });
      
      user_feedback = '';
      //I'm fine with not clearing the from field
    }
  });

  function fill_previous_feedback(){
    //console.log('fill_previous_feedback');
    var cur_input = $('#feedback_textarea');
    var cur_from = $('#feedback_from_textarea');
    if(cur_input.length > 0){
      cur_input.val(user_feedback);
    }
    if(cur_from.length > 0){
      cur_from.val(from_feedback);
    }
  }

  function delayed_show(popup_state_when_posted){
    if(!validPopupState(popup_state_when_posted)) return;
    //console.log('delayed_show');
    var el = $('#feedback_link');
    el.popover('show');
  }

  function delayed_hide(popup_state_when_posted){
    if(!validPopupState(popup_state_when_posted)) return;

    //console.log('delayed_hide');
    var el = $('#feedback_link');
    el.popover('hide');

  }

  function show_result(template, title, popup_state_when_posted){
    if(!validPopupState(popup_state_when_posted)) return;

    //console.log('show_result');
    var el = $('#feedback_link');
    var template = $('#' + template).html().trim();
    el.removeAttr('data-set');
    el.attr('data-content', template);
    el.attr('data-original-title',title);
    // For some reason this damn popover is hiding randomly, look into it when I have interwebs
    setTimeout(delayed_show, 150, popup_state_when_posted);
    setTimeout(delayed_hide, 6000, popup_state_when_posted);
  }

  function validPopupState(popup_state_when_posted){
    // If they've started to send another message or something, we don't interrupt
    var goodState = popup_state_when_posted == current_popup_state;
    if(!goodState) Logger.timestamp('Popup state no longer valid, current: ' + current_popup_state + ' posted state: ' + popup_state_when_posted );
    return goodState;

  }

});


/*
 * Cart stuff
 */
$(function(){

  function create_cart(click_url, pics) {
    var iso_cart = $($("#iso_cart"));

    // Clear everything that was in there,
    // and provide the link
    iso_cart.html("<a href='"+ click_url + "'>Edit cart contents</a><br/>");

    for(var i = 0; i < pics.length; i++) {
      iso_cart.append("<img class='item' src=" + pics[i].thumbnail_url + ">")
    }
  }

  $("#cart_link").click( function(e) {
      var el = $(this);
      var template = $('#cart_form').html().trim();
      //el.attr('data-set', users_entered_data);
      el.attr('data-content', template);
      el.attr('data-original-title','Pictures in your cart');
      el.popover('toggle');

      // Now we've got the popover created. We just need to call the provided URL and asynchronously load some masonry
      var url = $("#cart_link").attr('album-pics-url')
      $.getJSON( url, function( json ) {
        create_cart(json.url, json.pics);
      });
      // stop it from navigating to the href
      e.preventDefault();
  });


});

/*
 * Notification stuff
 */
$(function(){
  $('#clearAllNotifications').on('click', function(){
    var notifications = $('.notification-class'),
        top = $(notifications[0]).data('notification_id'),
        call;

    call = $.ajax('/clear_notifications/' + top);
    call.done(function(results){
      if(results && results.ok){
        $('.notification-class.unread').removeClass('unread');
        $('#notification_count').text("");
        $('.clearAllNotifications').remove();
      } else {
        alert('an error has occurred');
      }
    });

    call.fail(function(){
        alert('an error has occurred');
    });
  });
});
