var user_feedback = "";

function feedback(el){
  el = $(el);
  var set = el.attr('data-set');
  set = Boolean(set); //anything that isn't blank is true to me!

  var cur_input = $('#feedback_textarea');
  if(cur_input.length > 0){
    user_feedback = $.trim(cur_input.val());
    console.log('setting feedback');
  }else{
    if(user_feedback!= ''){
      setTimeout(function(){ fill_previous_feedback()}, 20);
    }
  }

  if(!set){
    el.popover({ html : true });
    var template = $('#feedback_form').html().trim();
    el.attr('data-content', template);
    el.popover('show');
    el.attr('data-set', 'moo');
  }
}

function fill_previous_feedback(){
  var cur_input = $('#feedback_textarea');
  if(cur_input.length > 0){
    cur_input.val(user_feedback);
  }
}

function submit_feedback(){
  var cur_input = $('#feedback_textarea');
  if(cur_input.length > 0){
    user_feedback = $.trim(cur_input.val());
    var el = $('#feedback_link');
    el.popover('hide');
    var CSRF_TOKEN = $('input[name=csrfmiddlewaretoken]').attr('value');

    var json_data = JSON.stringify(
      {
        "user_feedback" : user_feedback,
      }
    );
      
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
        dynamicReaction(data, this_model);
      },
    });
    
    user_feedback = '';
    
  }
}
