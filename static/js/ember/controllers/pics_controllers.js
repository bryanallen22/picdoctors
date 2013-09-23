Pd.PicsController = Ember.ArrayController.extend({

});

Pd.PicsEditController = Ember.ArrayController.extend({
  itemController: 'pic'

});

Pd.PicsViewController = Ember.ArrayController.extend({
  itemController: 'pic'
});

Pd.PicController = Ember.ObjectController.extend({

  createMarkup: function(){
    var store = this.get('store'),
        pic = this.get('model');

    return store.createRecord(Pd.Markup, {pic: pic});
  },

  picStyle: function(){
    var url = this.get('preview_url'),
        width = this.get('width'),
        height = this.get('height'),
        uuid = this.get('uuid'),
        backgroundStyle = "background: url('" + url + "');",
        finished = this.get('finished'),
        style = "no-repeat;";

    if(!finished) style += "cursor: crosshair;";

    style += backgroundStyle;
    style += "width:" + width + "px;";
    style += "height:" + height + "px;";

    return style;
  }.property('preview_url', 'width', 'height', 'uuid', 'finished'),

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
