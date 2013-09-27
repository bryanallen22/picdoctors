Pd.PicsController = Ember.ArrayController.extend({});

Pd.PicsEditController = Ember.ArrayController.extend({
  itemController: 'pic'
});

Pd.PicsViewController = Ember.ArrayController.extend({
  itemController: 'pic'
});

Pd.PicController = Ember.ObjectController.extend({
  needs:['album'],

  isAlbumOwner: function(){
    return this.get('controllers.album.isAlbumOwner');
  }.property('controllers.album.isAlbumOwner'),

  isAlbumDoctor: function(){
    return this.get('controllers.album.isAlbumDoctor');
  }.property('controllers.album.isAlbumDoctor'),

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

  _save: function(){
    var model = this.get('model');
    // only save if dirty
    if(model.get('isDirty')){
      model.save().then(function(){
        Pd.Logger.timestamp('Saved pic instruction: ' + newMarkup.get('instruction'), 5); 
      },
      function(){
        Pd.Logger.timestamp('Failed to save pic instruction, should revert here!!!!!', 4); 
      });
    }
  },

  actions: {
    saveMeFocus: function(){
      // only save after 200 milliseconds of not focus outing(or typing)
      Ember.run.debounce(this,  this._save, 200);
    },
    saveMeKeyUp: function(){
      // only save after 10 seconds of not typing
      Ember.run.debounce(this,  this._save, 10000);
    }
  }

});
