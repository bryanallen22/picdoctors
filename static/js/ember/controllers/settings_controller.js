Pd.SettingsController = Em.ObjectController.extend({

});

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

Pd.SettingsEmailConfigController = Ember.ObjectController.extend({
  needs:'settings',
  user: Em.computed.alias('controllers.settings'),

  saveDisabled: function(){
    this.setProperties({saved:false, failedSave:false});
    return !this.get('isDirty');
  }.property('isDirty'),
  
  actions:{
    save:function(){
      var self = this;

      self.set('failed', false);
      this.get('model').save().then(function(record){
        Em.run.next(function(){
          self.set('saved', true);
        });
      }).catch(function(){
        Em.run.next(function(){
          self.set('failedError', 'An error occurred saving');
          self.set('failed', true);
        });
      });
    }
  }
});

Pd.SettingsRolesController = Ember.ObjectController.extend({
  availableRoles: ['doctor', 'user'],
  vError:'',
  vSaved:false,

  resetAlerts: function(){
    this.set('vError', "");
    this.set('vSaved', false);
  },

});

Pd.RoleController = Ember.ObjectController.extend({
  needs: ['settingsRoles'],

  roles: Ember.computed.alias('controllers.settingsRoles.roles'),

  userRole: function(){
    var name = this.get('model'),
    role = this.get('roles').findBy('name', name);
    return role;
  }.property('roles.@each.name'),

  actions:{
    remove: function(role){
      var roles = this.get('roles'),
      pc = this.parentController;
      pc.resetAlerts();
      role.deleteRecord();
      role.save().then(function(){
        pc.set('vSaved', true);
       // alert('saved');
      }, function(){
        //failed to save, do we alert them?
        pc.set('vError', 'Error communicating with server');
        role.rollback();
        roles.pushObject(role);
      });
    },
    add: function(roleName){
      var user = this.get('controllers.settingsRoles.model'),
          record = this.store.createRecord('role', {name:roleName, user:user}),
          roles = this.get('roles'),
          pc = this.parentController;
      pc.resetAlerts();


      record.save().then(function(result){
        pc.set('vSaved', true);
      }, function(){
        pc.set('vError', 'Error communicating with server');
      });
    }
  }
});
