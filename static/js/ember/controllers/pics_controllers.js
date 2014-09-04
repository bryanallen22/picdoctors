Pd.PicsController = Ember.ArrayController.extend({});

Pd.PicsEditController = Ember.ArrayController.extend({
  itemController: 'pic'
});

Pd.PicsViewController = Ember.ArrayController.extend({
  itemController: 'pic'
});

Pd.PicController = Ember.ObjectController.extend({
  needs:['album'],

  isAlbumOwner: Em.computed.alias('controllers.album.isAlbumOwner'),

  isAlbumDoctor: Em.computed.alias('controllers.album.isAlbumDoctor'),

  createMarkup: function(){
    var store = this.get('store'),
        pic = this.get('model');

    return store.createRecord(Pd.Markup, {pic: pic});
  },

  deselectAllMarkups: function(){
    this.get('model').deselectAllMarkups();
  },

  selectAllMarkups: function(){
    this.get('model').selectAllMarkups();
  },

  // this method is only called from the debounce, 
  // it's sets the context of the call to the model
  // this allows us to not worry about some race condition
  // of switching the page, and the model being different etc
  // we want to save this model!  but we want to debounce it
  _save: function(){
    var model = this; 
    // only save if dirty
    if(model.get('isDirty')){
      model.save().then(function(){
        Pd.Logger.timestamp('Saved pic instruction: ' + model.get('description'), 5); 
      },
      function(){
        Pd.Logger.timestamp('Failed to save pic instruction, should revert here!!!!!', 4); 
      });
    }
  },

  actions: {
    saveMeFocus: function(){
      // only save after 200 milliseconds of not focus outing(or typing)
      Ember.run.debounce(this.get('model'),  this._save, 200);
    },
    saveMeKeyUp: function(){
      // only save after 10 seconds of not typing
      Ember.run.debounce(this.get('model'),  this._save, 10000);
    }
  }

});
