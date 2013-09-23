attr = DS.attr;
belongsTo = DS.belongsTo;
hasMany = DS.hasMany;

Pd.Pic = DS.Model.extend({
  group: belongsTo('group'),
  markups: hasMany('markup'),
  description: attr(),
  preview_url: attr(),
  width: attr(),
  height: attr()
});

Pd.Pic.reopen({
  finished: function(){
    return this.get('group.finished');
  }.property('group.finished'),


  deselectAllMarkups: function(){
    this.get('markups').forEach(function(markup){
      markup.set('selected', false);
    });
  },

  selectAllMarkups: function(){
    this.get('markups').forEach(function(markup){
      markup.set('selected', true);
    });
  },

});
