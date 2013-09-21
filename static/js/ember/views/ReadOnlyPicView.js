// Just in case you're wondering, this uses whatever controller called him,
// currently since it's only used once, it's the pic controller (because
// the picS (note the s) controller has an itemController="pic"
Pd.ReadOnlyPicView = Ember.View.extend({

  templateName: 'pic_span',
  didInsertElement: function() {
    this._super();
  },

  picsMarkups: function(){
    return this.get('content.markups');
  }.property('content.markups'),

  picSpan: function(){
    return this.$().find('.markup_pic_container');
  }.property('content')

});
