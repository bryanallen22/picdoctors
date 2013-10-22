Pd.MarkupVisualView = Ember.View.extend({
  templateName: 'markup_visual',
  didInsertElement: function() {
    this._super();
    
    var markup = this.get('controller.model');
    
    if(!markup.get('finished')) return;


    var description = markup.get('description'),
        markupStyle = markup.get('markupStyle'),
        colorName = markupStyle.get('name'),
        title = colorName + ' area instructions';

    if(Ember.isEmpty(description)){
      description = "No instruction";
    }

    this.$().popover(
      {
         placement :"right",
         title : title,
         content: description,
         trigger: "hover",
      });
  }

});

