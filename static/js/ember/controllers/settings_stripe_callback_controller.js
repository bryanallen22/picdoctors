Pd.SettingsStripeCallbackController = Em.ObjectController.extend({
  needs:'settings',
  user: Em.computed.alias('controllers.settings.model'),
  step1: 'Pending',
  step2: 'Pending',
  showLoader:true,
  showStep2:false, 

  hookupStripe: function(){
    var self = this;
    
    if(this.isError()) return;
    this.set('step1', 'Doing');

    postTo('/api/hookup_stripe', this.get('model'), 
      function(response){
        self.set('user.stripe_user', response.stripe_user);
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
