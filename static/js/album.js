$(function(){

  var CSRF_TOKEN = $('input[name=csrfmiddlewaretoken]').attr('value');
  
  var RemoteControl = Backbone.View.extend({
    events: {
 //     'click       .before_button': 'before_click',
 //     'click       .after_button':  'after_click',
    },

    initialize: function() {
    },

  });

  var CombinationView = Backbone.View.extend({
    initialize: function() {
      var rc_el = this.$el.find('.remote_control');
      this.remote_control = new RemoteControl({el: rc_el});

      this.before_after = this.$el.find('.picbeforeafter');
      this.before_after.qbeforeafter({defaultgap:50, leftgap:0, rightgap:10, caption: false, reveal: 0.5});
  //    this.remote_control.before = this.$el.find('.before');
  //    this.remote_control.after = this.$el.find('.after');
  //    this.remote_control.before_button = this.$el.find('.before_button');
  //    this.remote_control.after_button = this.$el.find('.after_button');
    },

  });

  $(".combination").each( function(){
    var cb = new CombinationView({el:this});
  });

  var ApprovalView = Backbone.View.extend({
    initialize: function() {

    },

    events: {
      'click       .btn_approve_all': 'approve_all',
      'click       .btn_accept_job':  'accept_job',
    },

    approve_all: function(){

      var json_data = JSON.stringify(
        {
          "job_id" : this.$el.attr('job_id'),
        }
      );
      
      $.ajax({
        headers: {
          "X-CSRFToken":CSRF_TOKEN
        },
        type: 'POST',
        url:  '/approve_album/',
        data: json_data,
        success : function(data, textStatus) {
          console.log(data);
          console.log(textStatus);
          location.href = data.redirect;
        }
      });
    },

    accept_job: function(){

      var json_data = JSON.stringify(
        {
          "job_id" : this.$el.attr('job_id'),
        }
      );
      
      $.ajax({
        headers: {
          "X-CSRFToken":CSRF_TOKEN
        },
        type: 'POST',
        url:  '/accept_doctors_work/',
        data: json_data,
        success : function(data, textStatus) {
          console.log(data);
          console.log(textStatus);
          location.href = location.href;
        }

      });
    },

  });

  var av_el = $(".album_control");
  var av = new ApprovalView({el:av_el});


});
