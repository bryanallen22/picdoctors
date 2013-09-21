attr = DS.attr;
belongsTo = DS.belongsTo;
hasMany = DS.hasMany;

Pd.Markup = DS.Model.extend({
  pic: belongsTo('pic'),
  description: attr(),
  height: attr(),
  left: attr(),
  top: attr(),
  width: attr(),

  toStringExtension: function(){
    return this.get('description');
  }
});

Pd.Markup.reopen({
  selected: false,
  markupStyle: null,
  deletable: true,

  finished: function(){
    return this.get('pic.finished');
  }.property('pic.finished')
});

Pd.MarkupStyle = DS.Model.extend({
  name: attr(),
  color: attr(),
  border_style:attr()
});
