Pd.SettingsRolesController = Ember.ObjectController.extend({
  availableRoles: ['doctor', 'user'],
  vError:'',
  vSaved:false,

  resetAlerts: function(){
    this.set('vError', "");
    this.set('vSaved', false);
  },
  actions:{
    refresh: function(){
       window.location.reload();
    }
  }

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
      roles.removeObject(role);
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


