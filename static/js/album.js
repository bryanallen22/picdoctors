$(function(){
  
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
