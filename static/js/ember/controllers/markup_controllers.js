Pd.MarkupsController = Ember.ArrayController.extend({});

// TODO think up a better name for this
Pd.EditableCommentsController = Ember.ArrayController.extend({});

Pd.MarkupDescriptionEditController = Ember.ObjectController.extend({
  _save: function(){
    var model = this.get('model');
    if(model.get('isDirty')){
      model.save();
    }
  },

  actions: {
    saveMeFocus: function(){
      // only save after 20 milliseconds of not focus outing
      Ember.run.debounce(this, this._save, 20);
    },
    saveMeKeyUp: function(){
      var self = this;
      // only save after 10 seconds of not typing
      Ember.run.debounce(this,  this._save, 10000);
    }
  }

});

Pd.EditableMarkupController = Ember.ObjectController.extend({
  markupStyleCss: function(){
    var left = this.get('left'),
        top = this.get('top'),
        height = this.get('height'),
        width = this.get('width'),
        markupStyle = this.get('markupStyle'),
        color = markupStyle.get('color'),
        style = "border: 4px " + color + ";",
        borderStyle = markupStyle.get('border_style');

    style += "left: " + left + "px;";
    style += "height: " + height + "px;";
    style += "width: " + width + "px;";
    style += "top: " + top + "px;";
    style += "border-style: " + borderStyle + ";" ;
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
