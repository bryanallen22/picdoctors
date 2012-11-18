var user_feedback = "";
var from_feedback = "";
//for use if they start to add feedback again while we are showing off our thank you
var show_user_result = false;

function feedback(el){
  show_user_result = false;

  console.log('feedback');
  el = $(el);
  var set = el.attr('data-set');
  set = Boolean(set); //anything that isn't blank is true to me!


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

  if(!set){
    el.popover({ html : true });
    var template = $('#feedback_form').html().trim();
    el.attr('data-set', 'moo');
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
      
    show_user_result=true;
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
        if(!show_user_result)
          return;
        if(data.success){
          show_result('feedback_thanks', 'Feedback Submitted');
        } else {
          show_result('feedback_thanks_but', 'Feedback Not Submitted');
        }
      },
    });
    
    user_feedback = '';
    //I'm fine with not clearing the from field
  }
}

function show_result(template, title){
  console.log('show_result');
  var el = $('#feedback_link');
  var template = $('#' + template).html().trim();
  el.attr('data-content', template);
  el.attr('data-original-title',title);
  el.popover('show');
  el.removeAttr('data-set');
  setTimeout('delayedHide()',3000);
}

function delayedHide(){
  if(!show_user_result)
    return;

  console.log('delayed_hide');
  var el = $('#feedback_link');
  el.popover('hide');

}
