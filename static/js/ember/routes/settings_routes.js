Pd.SettingsRoute = Em.Route.extend({
  model: function(){
    return this.modelFor('application');
  },
  afterModel: function(model, transition){
    // this is where you'd redirect if they aren't logged in
    if(!model.get('isLoggedIn')){
      transition.abort();
      window.location.href = '/';
    }
  }
});

Pd.SettingsIndexRoute = Em.Route.extend({
  redirect: function(){
    this.transitionTo('settings.profile');
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

Pd.SettingsCreditcardsRoute = Em.Route.extend({
  model: function(){
   var result = this.get('creditcard') || this.store.find('creditcard');
   this.set('creditcard', result);
   return result;
  }
});

Pd.SettingsPaymentsRoute = Em.Route.extend({
  model: function(){
    return this.modelFor('settings');
  }
});

Pd.SettingsStripeCallbackRoute = Em.Route.extend({
  model : function() {
    return {
        scope: Pd.getQueryParam('scope'),
        code: Pd.getQueryParam('code'),
        error: Pd.getQueryParam('error'),
        error_description: Pd.getQueryParam('error_description')
    };
  },
  setupController: function(controller, model){
    this._super(controller, model);
    Em.run.next(controller, controller.hookupStripe);
  }
});

