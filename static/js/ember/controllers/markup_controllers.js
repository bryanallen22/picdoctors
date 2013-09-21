Pd.MarkupsController = Ember.ArrayController.extend({});

Pd.MarkupInstructionsController = Ember.ArrayController.extend({
  itemController: 'markupInstruction'
});

Pd.MarkupInstructionController = Ember.ObjectController.extend({
  descStyle: function(){

    var markupStyle = this.get('markupStyle'),
        color = markupStyle.get('color'),
        style = "border: 4px " + color + ";",
        borderStyle = markupStyle.get('border_style');

    style += "border-style: " + borderStyle + ";" ;
    return style;
  }.property('markupStyle')

});

// TODO which one is this one?
// I mean, I realize it's for saving a markup instruction
Pd.MarkupInstructionTextBoxController = Ember.ObjectController.extend({
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

Pd.MarkupVisualController = Ember.ObjectController.extend({
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
  }.property('left', 'top', 'height', 'markupStyle'),
})


