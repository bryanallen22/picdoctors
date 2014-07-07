Pd.SettingsCreditcardsController = Ember.ArrayController.extend({
  vError:'',
  vSaved:false,
  vDeleting:false,

  resetAlerts: function(){
    this.set('vError', "");
    this.set('vSaved', false);
    this.set('vDeleting', false);
  },

  actions:{
    deleteCard: function(card){
      var self = this;
      self.resetAlerts();
      self.set('vDeleting', true);
      card.destroyRecord().then( function(record) {
        // success
        self.set('vDeleting', false);
        self.set('vSaved', true);
      }, function(record) {
        // failure
        self.set('vDeleting', false);
        self.set('vError', 'Uh oh! There was a problem deleting your card!');
      });
    },
  },
});

Pd.CreditcardController = Ember.ObjectController.extend({ });

