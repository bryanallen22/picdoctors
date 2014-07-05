Pd.SettingsCreditcardsController = Ember.ArrayController.extend({
  actions:{
    delete: function(id){
      console.log("Deleting card " + id);
      var card = this.store.find('creditcard', id);

      // http://emberjs.com/guides/models/creating-and-deleting-records/
      //card.deleteRecord(); -- does not exist
      //card.destroyRecord(); -- does not exist
      card.destroy(); // doesn't seem to do anything
    }
  },
});

Pd.CreditcardController = Ember.ObjectController.extend({ });

