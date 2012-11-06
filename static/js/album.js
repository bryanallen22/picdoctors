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

    //template:  _.template($('#message_template').html().trim()),

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
  var hard_code_blank = 'Write your message here';
  
  var MessageInput = Backbone.View.extend({
    
    events: {
      'keypress    .message_input': 'checkKey',
      'blur        .message_input': 'onblur',
      'focus       .message_input': 'onfocus',
    },

    initialize: function(){
    },

    render: function(){
      // Compile the template using underscore
    },

    checkKey: function(ev){
      if(ev.which == 13){
        var src = $(ev.target);
        if(src.val().trim()!='')
          this.postMessage.call(this, src);
      }
    },

    onblur: function(ev){
      var el = ev.target;
      if(el.value=='') 
        el.value=hard_code_blank;
    },

    onfocus: function(ev){
      var el = ev.target;
      if(el.value==hard_code_blank) 
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


  var RemoteControl = Backbone.View.extend({
    events: {
      'click       .before_button': 'before_click',
      'click       .after_button':  'after_click',
    },

    initialize: function() {
    },

    before_click: function() {
      this.before.css('display', 'inherit');
      this.after.css('display', 'none');
      this.before_button.removeClass('btn-primary');
      this.after_button.addClass('btn-primary');
    },

    after_click: function() {
      this.before.css('display', 'none');
      this.after.css('display', 'inherit');
      this.before_button.addClass('btn-primary');
      this.after_button.removeClass('btn-primary');
    },

  });

  var CombinationView = Backbone.View.extend({
    initialize: function() {
      var rc_el = this.$el.find('.remote_control');
      this.remote_control = new RemoteControl({el: rc_el});
      this.remote_control.before = this.$el.find('.before');
      this.remote_control.after = this.$el.find('.after');
      this.remote_control.before_button = this.$el.find('.before_button');
      this.remote_control.after_button = this.$el.find('.after_button');
    },

  });

  $(".combination").each( function(){
    var cb = new CombinationView({el:this});
  });

});
