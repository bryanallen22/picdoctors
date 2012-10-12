$(function(){
  

  var true_sync_func = Backbone.sync;
  var CSRF_TOKEN = $('input[name=csrfmiddlewaretoken]').attr('value');
  Backbone.sync = function(method, model, options){
    options.beforeSend = function(xhr){
      xhr.setRequestHeader('X-CSRFToken', CSRF_TOKEN);
    };
    return true_sync_func( method, model, options);
  };

  var Message = Backbone.Model.extend({
    // Default attributes for the Message Model
    defaults: function() {
      return {
        message:      '',
        created:      null,
        commentor:    '',
      };
    },
    
    initialize : function() {
    },

    clear: function() {
      this.destroy();
    },

  });

  // A collection of Message elements
  var MessageList = Backbone.Collection.extend({

    // Reference to this collection's model.
    model: Message,

    // Url base
    url: '/message_handler/',

    initialize: function() {
      this.container = null; // Will be set to contact_arena element
    },

  });

  $(".contact_arena").each( function(){
    var ml = new MessageList();
    ml.container = this;
  });

  
  $(".message_input").each( function(){
    el = this;
    $(this).keypress(postMessage);

  });  

  function postMessage(ev){
    if(ev.which == 13){
      var src = $(ev.srcElement);
      var message = src.val();
      var group_id = src.attr('group_id');
      var job_id = src.attr('job_id');
      var json_data = JSON.stringify(
        {
          "job_id" : job_id,
          "group_id" : group_id, 
          "message" : message,
        }
      );
      src.attr('disabled', 'disabled');
      $.ajax({
        headers: {
          "X-CSRFToken":CSRF_TOKEN
        },
        type: 'POST',
        url:  '/post_message/',
        data: json_data,
        success : function(data, textStatus) {
          console.log(data);
          console.log(textStatus);
          create_message(src, message);
          src.val('');
          src.removeAttr('disabled');
        },
        failure : function(jqXHR, textStatus, errorThrown) {
          console.log(jqXHR);
          console.log(textStatus);
          console.log(errorThrown);
          src.removeAttr('disabled');
        }

      });
    }
  }

  function create_message(src, info) {
    var arena = src.closest('.contact_arena').find('.messages_arena');
    arena.append(info);
  }





});
