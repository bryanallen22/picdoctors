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

Pd.SettingsStripeCallbackController = Em.ObjectController.extend({
  step1: 'Pending',
  step2: 'Pending',
  showLoader:true,
  showStep2:false, 

  hookupStripe: function(){
    var self = this;
    
    if(this.isError()) return;
    this.set('step1', 'Doing');

    postTo('/api/hookup_stripe', this.get('model'), 
      function(){
        self.set('step1', 'Done');
        self.complete();
      },
      function(response){
        self.set('step1', 'Failed');
        self.fail('There was an error connecting your Stripe Connect account'); 
      });
  },
  isError: function(){
    var model = this.get('model'),
    error = !model.code || (model.error || model.error_description),
    msg = model.error_description || model.error || 'Missing Access Token';

    msg = msg.replace(/\+/g, " ");

    if(error){
      this.set('step1', 'Error');
      this.fail(msg); 
    }

    return error;
  },
  complete: function(){
    this.set('showLoader', false);
    this.set('showStep2', true);
  },

  fail: function(error){
    this.set('showLoader', false);
    this.set('vError', error);
  },
  actions:{
    goNewJobs: function(){
      window.location.href = '/new_jobs';
    }
  }
});
