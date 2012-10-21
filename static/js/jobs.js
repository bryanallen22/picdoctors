// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

  var true_sync_func = Backbone.sync;
  var CSRF_TOKEN = $('input[name=csrfmiddlewaretoken]').attr('value');
  Backbone.sync = function(method, model, options){
    options.beforeSend = function(xhr){
      xhr.setRequestHeader('X-CSRFToken', CSRF_TOKEN);
    };
    return true_sync_func( method, model, options);
  };

  var JobRow = Backbone.View.extend({

    el: '',


    initialize: function(){
      this.job_id=this.$el.attr('job_id');
    },

    events: {
      "click .dynamic_action_button" : "executeDynamicAction",
    },

    executeDynamicAction: function(event){
      var postback_url = $(event.target).attr('postback_url');
      var redir_val = $(event.target).attr('redir').toLowerCase();

      console.log('execute dynamic action: ' + postback_url);

      if(redir_val == 'true') {
        location.href = postback_url;
        return;
      }

      var json_data = JSON.stringify(
        {
          "job_id" : this.job_id,
        }
      );
      
      $.ajax({
        headers: {
          "X-CSRFToken":CSRF_TOKEN
        },
        type: 'POST',
        url:  postback_url ,
        data: json_data,
        success : function(data, textStatus) {
          console.log(data);
          console.log(textStatus);
      //    location.href = "/jobs";
          dynamicReaction(data);
        },
        failure : function(jqXHR, textStatus, errorThrown) {
          console.log(jqXHR);
          console.log(textStatus);
          console.log(errorThrown);
        }

      });

    },

  })

  function dynamicReaction(data) {
   var actions = data.actions;
   for (var i = 0; i < actions.length; i++) {
     var action = actions[i];
     switch(action.action)
     {
      case 'alert':
        $(".alert_row").text(action.data);
        animatedcollapse.show('alert_section'); 
        break;
      case 'reload':
        location.href = location.href;
        break;
      case 'redirect':
        location.href = action.data;
        break;
      case 'delay_redirect':
        delay_redirect(action.data);
        break;
      case 'remove_job_row':
        remove_row_by_job_id(action.data);
        break;
      default:
        alert('Implementation failure for "' + action.action + '" with the data: "' + action.data + '"');
        break;
     }
   }
  }

  function remove_row_by_job_id(job_id){
    $('.job_row').each(function(){
      if($(this).attr('job_id') == job_id){
        $(this).remove();
      }
    });
  }

  function delay_redirect(data){
        continue_redirect = true;
        //Build the button template only once, that way you can click the buttons
        template = _.template( $('#redirect_buttons_template').html() );
        $(".redirect_row_buttons").html( this.template( { }));

        //Start the redirect loop
        redirect_time(10.1, data.href, data.view);
  }
  
  continue_redirect = true;
  redirect_now = false;
  function redirect_time(time_left, new_loc, view){
    if(continue_redirect==false) {
      $(".redirect_row").html("");
      $(".redirect_row_buttons").html("");
      return;
    }
    if(redirect_now){
      time_left = 0;
    }
    if(time_left<=0){
      location.href = new_loc;
    } else {
      time_left = time_left - 0.1;
      template = _.template( $('#redirect_template').html() );
      //$(".redirect_row").text('You will automatically be redirected to ' + view + ' in ' + time_left + ' second(s)');
      $(".redirect_row").html( this.template(
          {
            view      : view,
            time_left : Math.round(time_left),
          }));

      setTimeout(function(){redirect_time(time_left, new_loc, view)}, 100);
    }
  }


  var JobView = Backbone.View.extend({

    el: $("#job_app"),


    initialize: function() {

      $(".job_row").each( function() {
        new JobRow({el:$(this)});
      });
    },

    render: function() {
        console.log('render job view');
    },

  });

  var Jobs = new JobView;

});
