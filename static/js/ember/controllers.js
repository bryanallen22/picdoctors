Pd.ApplicationController = Ember.ObjectController.extend({});

Pd.AlbumsController = Ember.ArrayController.extend({});
Pd.AlbumController = Ember.ObjectController.extend({});

Pd.GroupsController = Ember.ArrayController.extend({});
Pd.GroupController = Ember.ObjectController.extend({});

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
      var self = this;
      // only save after 20 milliseconds of not focus outing
      Ember.run.debounce(this, function(){ self._save();}, 20);
    },
    saveMeKeyUp: function(){
      var self = this;
      // only save after 10 seconds of not typing
      Ember.run.debounce(this,  this._save, 10000);
    }
  }

});

Pd.MarkupsController = Ember.ArrayController.extend({});
Pd.EditableCommentsController = Ember.ArrayController.extend({

});

Pd.MarkupDescriptionEditController = Ember.ObjectController.extend({
  _save: function(){
    var model = this.get('model');
    if(model.get('isDirty')){
      model.save();
    }
  },

  actions: {
    saveMeFocus: function(){
      var self = this;
      // only save after 20 milliseconds of not focus outing
      Ember.run.debounce(this, function(){ self._save();}, 20);
    },
    saveMeKeyUp: function(){
      var self = this;
      // only save after 10 seconds of not typing
      Ember.run.debounce(this,  this._save, 10000);
    }
  }

});
Pd.EditableMarkupController = Ember.ObjectController.extend({
  markupStyle: function(){
    var left = this.get('left'),
        top = this.get('top'),
        height = this.get('height'),
        width = this.get('width'),
        style = "border: 4px green;";

    style += "left: " + left + "px;";
    style += "height: " + height + "px;";
    style += "width: " + width + "px;";
    style += "top: " + top + "px;";
    style += "border-style: solid;";
    return style;
  }.property('left', 'top', 'height')
})


Pd.MarkupNavigationController = Ember.ObjectController.extend({
  needs:['application'],

  setupGroups: function(){
    var current = this.get('model'),
        currentIdx = 0,
        groups = current.get('album.groups'),
        len = groups.get('length'),
        next,
        previous = current;


    for(var i = 0; i<len; i++){
      var group = groups.objectAt(i);
      if(group === current){
        currentIdx = i;
        break;
      }    
    }

    this.set('_previousGroup', null);
    this.set('_nextGroup', null);

    if(currentIdx>0){
      this.set('_previousGroup', groups.objectAt(currentIdx-1));
    }

    if(currentIdx+1<len){
      this.set('_nextGroup', groups.objectAt(currentIdx+1));
    }
  }.property('model'),

  _nextGroup: null,
  
  nextGroup: function(){
    this.get('setupGroups');
    return this.get('_nextGroup');    
  }.property('model', '_nextGroup'),

  _previousGroup: null,

  previousGroup: function(){
    this.get('setupGroups');
    return this.get('_previousGroup');    
  }.property('model', '_previousGroup'),

  isLoggedIn: function(){
    return this.get('controllers.application.isLoggedIn');
  }.property('controllers.application.isLoggedIn')

});

