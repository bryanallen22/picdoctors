var user_feedback = "";
var from_feedback = "";
//for use if they start to add feedback again while we are showing off our thank you
var current_popup_state = 1;

var users_entered_data = true;

function feedback_link_click(el){
  current_popup_state += 1;

  console.log('feedback');
  el = $(el);
  var data_set = el.attr('data-set');
  data_set = Boolean(data_set); //anything that isn't blank is true to me!


  var cur_input = $('#feedback_textarea');
  var cur_from = $('#feedback_from_textarea');
  if(cur_input.length > 0){
    user_feedback = $.trim(cur_input.val());
    from_feedback = $.trim(cur_from.val());
    console.log('setting feedback');
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
}

function fill_previous_feedback(){
  console.log('fill_previous_feedback');
  var cur_input = $('#feedback_textarea');
  var cur_from = $('#feedback_from_textarea');
  if(cur_input.length > 0){
    cur_input.val(user_feedback);
  }
  if(cur_from.length > 0){
    cur_from.val(from_feedback);
  }
}

function submit_feedback(){
  console.log('submit_feedback');
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
        console.log(data);
        console.log(textStatus);
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
}

function show_result(template, title, popup_state_when_posted){
  if(!validPopupState(popup_state_when_posted)) return;

  console.log('show_result');
  var el = $('#feedback_link');
  var template = $('#' + template).html().trim();
  el.removeAttr('data-set');
  el.attr('data-content', template);
  el.attr('data-original-title',title);
  // For some reason this damn popover is hiding randomly, look into it when I have interwebs
  setTimeout('delayed_show(' + popup_state_when_posted + ')',150);
  setTimeout('delayed_hide(' + popup_state_when_posted + ')',6000);
}

function delayed_show(popup_state_when_posted){
  if(!validPopupState(popup_state_when_posted)) return;
  console.log('delayed_show');
  var el = $('#feedback_link');
  el.popover('show');
}

function delayed_hide(popup_state_when_posted){
  if(!validPopupState(popup_state_when_posted)) return;

  console.log('delayed_hide');
  var el = $('#feedback_link');
  el.popover('hide');

}

function validPopupState(popup_state_when_posted){
  // If they've started to send another message or something, we don't interrupt
  var goodState = popup_state_when_posted == current_popup_state;
  if(!goodState) console.log('Popup state no longer valid, current: ' + current_popup_state + ' posted state: ' + popup_state_when_posted );
  return goodState;

}
