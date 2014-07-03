Pd.SettingsPasswordController = Ember.Controller.extend({
  old_password : null,
  new_password : null,
  confirm_password : null,

  // Swiches for showing errors:
  show_passwordmatch_error : false,
  password_changed : false,
  bad_oldpassword : false,

  validate_new_password : function() {
    this.set('show_passwordmatch_error', !this.get('matching_passwords'));
  },

  matching_passwords : function() {
    return this.get('new_password') == this.get('confirm_password');
  }.property('new_password', 'confirm_password'),

  watch_oldpassword : function() {
    this.set('bad_oldpassword', false);
  }.observes('old_password'),

  watch_newpasswords: function() {
    this.set('show_passwordmatch_error', false);
  }.observes('new_password', 'confirm_password'),

  actions : {
    save : function() {
      this.validate_new_password();
      if(this.get('matching_passwords')) {
        data = {
          'old_password'     : this.get('old_password'),
          'new_password'     : this.get('new_password'),
          'confirm_password' : this.get('confirm_password'),
        }
        var that = this;
        $.post('/change_password/', data, function(data, textStatus) {
          if(data.success == true) {
            that.set('password_changed', true);
            that.setProperties({old_password:'', new_password:'', confirm_password:''});
          }
          else if(data.bad_oldpassword == true) {
            that.set('bad_oldpassword', true);
          }
        });
      }
    }
  }
});
