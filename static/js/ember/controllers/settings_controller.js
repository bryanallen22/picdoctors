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

Pd.SettingsPaymentsController = Em.ObjectController.extend({
  stripeUrl: function(){
    var nick = this.get('nickname'),
        base = location.protocol + '//' + location.host,
        url = base + '/doctor_profile/' + nick,
        qp = {
      client_id: stripeClientId,
      response_type: 'code',
      scope: 'read_write',
      stripe_user:{
        email: this.get('email'),
        url: url,
        product_category:'art_and_graphic_design',
        product_description:'Image editing'
      }
    };
    return Pd.stripe_oauth + "?" + $.param(qp);
  }.property()

});

Pd.SettingsProfileController = Em.ObjectController.extend({
    invalidEmail: function(){
      var email = this.get('email');
      return !email.match(/^.+?\@.+?\..+$/);
    }.property('email'),

    saveDisabled: Em.computed.or('invalidEmail'),
    actions:{
      save: function(){
        var self = this;
        this.get('model').save().then(function(){
          self.set('saved', true);
        },function(error){
          self.set('failedError', 'An error occurred saving');
          self.set('failedSave', true);
        });
      }
    }
});

Pd.SettingsBeadoctorController = Em.ObjectController.extend({

});
