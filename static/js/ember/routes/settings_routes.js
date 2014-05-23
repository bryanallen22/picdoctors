Pd.SettingsRoute = Em.Route.extend({
  model: function(){
    return this.modelFor('application');
  }
});

Pd.SettingsProfileRoute = Em.Route.extend({
  model: function(){
    return this.modelFor('settings');
  }
});

Pd.SettingsPasswordRoute = Em.Route.extend({
  //d Don't have a model because we don't store passwords,
  // cause that would be dumb. Dan if fat.

});

Pd.SettingsEmailConfigRoute = Em.Route.extend({
  model : function() {
    var blah = this.modelFor('settings').get('emailConfig');
    console.log(blah);
    debugger;
    return this.modelFor('settings').get('emailConfig');
  }
});
