Pd.PicsController = Ember.ArrayController.extend({});

Pd.PicsEditController = Ember.ArrayController.extend({
  itemController: 'pic',
});

Pd.PicController = Ember.ObjectController.extend({
  picStyle: function(){
    var url = this.get('preview_url'),
        width = this.get('width'),
        height = this.get('height'),
        uuid = this.get('uuid'),
        backgroundStyle = "background: url('" + url + "');",
        style = "no-repeat;";

    style += backgroundStyle;
    style += "width:" + width + "px;";
    style += "height:" + height + "px;";

    return style;
  }.property('preview_url', 'width', 'height', 'uuid'),

  _save: function(){
    var model = this.get('model');
    if(model.get('isDirty')){
      model.save();
    }
  },

  actions: {
    saveMeFocus: function(){
      // only save after 20 milliseconds of not focus outing
      Ember.run.debounce(this,  this._save, 20);
    },
    saveMeKeyUp: function(){
      // only save after 10 seconds of not typing
      Ember.run.debounce(this,  this._save, 10000);
    }
  }

});
