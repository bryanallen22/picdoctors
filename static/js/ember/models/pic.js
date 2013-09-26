attr = DS.attr;
belongsTo = DS.belongsTo;
hasMany = DS.hasMany;

Pd.BasePic = DS.Model.extend({
  preview_url: attr(),
  width: attr(),
  height: attr()
});

Pd.Pic = Pd.BasePic.extend({
  group: belongsTo('group'),
  markups: hasMany('markup'),
  description: attr()
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

Pd.DocPic = Pd.BasePic.extend({
  group: belongsTo('group'),
  created: attr()
});

Pd.DocPic.reopen({
  finished: function(){
    return this.get('group.finished');
  }.property('group.finished'),

  formattedCreated: function(){
    var created = moment(this.get('created'));
    return created.calendar();
  }.property('created')
});
