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

Pd.SettingsMerchantInfoController = Em.Controller.extend({
  needs:'settings',
  user: Em.computed.alias('controllers.settings'),
  email: Em.computed.oneWay('user.email'),
  individual: 'true',
  showIndividual: Em.computed.equal('individual', 'true'),

  actions: {
    save: function(){
      var properties = this.getProperties(['name', 'ein', 'email']);
      postTo('/api/create_merchant', properties);


    }
  }
});
