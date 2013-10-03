Pd.MarkupsController = Ember.ArrayController.extend({
  itemController: 'markup',

  hasMarkups: function(){
    return this.get('length') > 0;
  }.property('length')
});

Pd.MarkupController = Ember.ObjectController.extend({
  markupStyleCss: function(){
    var left = this.get('left'),
        top = this.get('top'),
        height = this.get('height'),
        width = this.get('width'),
        markupStyle = this.get('markupStyle'),
        color = markupStyle.get('color'),
        style = "border: 4px " + color + ";",
        selected = this.get('selected'),
        borderStyle = markupStyle.get('border_style');

    style += "left: " + left + "px;";
    style += "opacity: " + (selected?"1":"0.3") + ";";
    style += "height: " + height + "px;";
    style += "width: " + width + "px;";
    style += "top: " + top + "px;";
    style += "border-style: " + borderStyle + ";" ;
    return style;
  }.property('left', 'top', 'height', 'markupStyle', 'selected')
});

Pd.MarkupInstructionsController = Ember.ArrayController.extend({
  itemController: 'markupInstruction'
});

Pd.MarkupInstructionController = Ember.ObjectController.extend({
  descStyle: function(){

    var markupStyle = this.get('markupStyle'),
        color = markupStyle.get('color'),
        selected = this.get('selected'),
        style = "border: 4px " + color + ";",
        borderStyle = markupStyle.get('border_style');

    style += "opacity: " + (selected?"1":"0.3") + ";";
    style += "border-style: " + borderStyle + ";" ;
    return style;
  }.property('markupStyle', 'selected')

});

Pd.MarkupInstructionTextBoxController = Ember.ObjectController.extend({

  // this method is only called from the debounce, 
  // it's sets the context of the call to the model
  // this allows us to not worry about some race condition
  // of switching the page, and the model being different etc
  // we want to save this model!  but we want to debounce it
  _save: function(){
    var model = this;
    if(model.get('isDirty')){
      Pd.Logger.timestamp('Saving markup: ' + model.get('id'), 5); 
      model.save().then(function(){
        Pd.Logger.timestamp('Saved new markup instruction: ' + newMarkup.get('instruction'), 5); 
      },
      function(){
        Pd.Logger.timestamp('Failed to save markup instruction, should revert here!!!!!', 4); 
      });
    }
  },

  actions: {
    focus: function(){
      var markup = this.get('model'),
          pic = markup.get('pic');
      pic.deselectAllMarkups();
      markup.set('selected', true);
    },

    saveMeFocusOut: function(){
      this.get('model.pic').selectAllMarkups();
      // only save after 200 milliseconds of not focus outing
      Ember.run.debounce(this.get('model'),  this._save, 200);
    },

    saveMeKeyUp: function(){
      // only save after 10 seconds of not typing
      Ember.run.debounce(this.get('model'),  this._save, 10000);
    }
  }

});
