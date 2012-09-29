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
        alert(action.data);
        break;
      case 'reload':
        location.href = location.href;
        break;
      case 'redirect':
        location.href = action.data;
        break;
      default:
        alert('Implementation failure for "' + action.action + '" with the data: "' + action.data + '"');
        break;
     }
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
