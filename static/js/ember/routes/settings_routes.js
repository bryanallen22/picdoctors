Pd.SettingsRoute = Em.Route.extend({
  model: function(){
    return this.modelFor('application');
  },
  afterModel: function(model, transition){
    // this is where you'd redirect if they aren't logged in
    if(!model.get('isLoggedIn')){
      alert('redirect to login');
    }
  }
});

Pd.SettingsProfileRoute = Em.Route.extend({
  model: function(){
    return this.modelFor('settings');
  }
});

Pd.SettingsPasswordRoute = Em.Route.extend({
  // password Don't have a model because we don't store passwords,
  // cause that would be dumb. Dan if fat.
});

Pd.SettingsEmailConfigRoute = Em.Route.extend({
  model : function() {
    return this.modelFor('settings').get('emailConfig');
  }
});

Pd.SettingsRolesRoute = Em.Route.extend({
  model: function(){
    return this.modelFor('settings');
  }
});
