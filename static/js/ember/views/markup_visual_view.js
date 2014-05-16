Pd.MarkupVisualView = Ember.View.extend({
  templateName: 'markup_visual',
  didInsertElement: function() {
    this._super();
    
    var markup = this.get('controller.model');
    
    if(!markup.get('finished')) return;


    var description = markup.get('description'),
        colorName = markup.get('markupStyle.name'),
        title = colorName + ' area instructions';

    if(Ember.isEmpty(description)){
      description = "No instruction";
    }

    this.$('.markup').popover(
      {
         placement :"right",
         title : title,
         content: description,
         trigger: "hover",
      });
  }

});

