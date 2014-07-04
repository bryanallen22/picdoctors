Pd.SettingsController = Em.ObjectController.extend({

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

Pd.SettingsFinancialsController = Em.Controller.extend({
  needs:'settings',
  user: Em.computed.alias('controllers.settings'),
  email: Em.computed.oneWay('user.email'),

  stripeUrl: function(){
    var qp = {
      client_id: stripeClientId,
      response_type: 'code',
      scope: 'read_write'
    };
    return Pd.stripe_oauth + "?" + $.param(qp);
  }.property()

});
