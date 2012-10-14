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
    // these must match server side for reset to work (or so it appears)
    defaults: function() {
      return {
        group_id  : -1,
        job_id    : -1,
        message   : '',
        created   : null,
        commentor : '',
        unseen    : '',
      };
    },
    
    initialize : function() {
    },

    clear: function() {
      this.destroy();
    },

  });

  var MessageView = Backbone.View.extend({
    
    className: 'message_row',

    template:  _.template($('#message_template').html().trim()),

    initialize: function(){
      this.render();
    },

    render: function(){
      // Compile the template using underscore
      
      this.$el.html(this.template(
        {
          group_id  : this.model.get('group_id'),
          job_id    : this.model.get('job_id'),
          message   : this.model.get('message'),
          created   : this.model.get('created'),
          commentor : this.model.get('commentor'),
          unseen    : this.model.get('unseen'),
        }
      ));
    }


  });
  
  var MessageInput = Backbone.View.extend({
    
    events: {
      'keypress    .message_input': 'checkKey',
      'blur      .message_input': 'onblur',
      'focus     .message_input': 'onfocus',
    },

    initialize: function(){
    },

    render: function(){
      // Compile the template using underscore
    },

    checkKey: function(ev){
      if(ev.which == 13){
        var src = $(ev.srcElement);
        if(src.val().trim()!='')
          this.postMessage.call(this, src);
      }
    },

    onblur: function(el){
      el = el.srcElement;
      if(el.value=='') 
        el.value='Write your message here';
    },

    onfocus: function(el){
      el = el.srcElement;
      if(el.value=='Write your message here') 
        el.value='';
    },


    postMessage: function(src){
        src.attr('disabled', 'disabled');
        var group_id = src.attr('group_id');
        var job_id = src.attr('job_id');
        var username = src.attr('username');
        var message = src.val();
        this.cur_message = this.message_list.create(
          {
            job_id    :       job_id,
            group_id  :       group_id,
            message   :       message,
            created   :       'Less than a minute ago',
            commentor :       username,
            unseen    :       'unseen'
          }
        );
        src.val('');
        src.removeAttr('disabled');
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
      this.bind('add', this.newMessage, this);
      this.bind('reset', this.setup, this);
    },


    newMessage: function (message){
      var view = new MessageView( { model: message } );
      this.container.append(view.el);
    },

    setup: function(){
      var that = this;
      this.each( function(el) {
        that.newMessage.call(that, el);
      });

    },

  });

  var MessageGrouping = Backbone.View.extend({
    initialize: function(){
      console.log('creating message group');
      this.message_list = new MessageList();
      this.message_list.container = this.$el.find('.message_arena');
      var input = this.$el.find('.message_input_arena');
      this.message_input = new MessageInput({el: input });
      this.message_input.message_list = this.message_list;
      var prev = this.$el.find('.previous_messages').html();
      this.message_list.reset( jQuery.parseJSON( prev ) );
      
    },
  });

  $(".contact_arena").each( function(){
    var mg = new MessageGrouping({el:this});
    mg.container = this;
    //message_lists.push(mg);
  });

});
