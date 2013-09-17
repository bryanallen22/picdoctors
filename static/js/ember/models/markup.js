attr = DS.attr;
belongsTo = DS.belongsTo;
hasMany = DS.hasMany;

Pd.Markup = DS.Model.extend({
  pic: belongsTo('pic'),
  description: attr(),
  height: attr(),
  left: attr(),
  pic: attr(),
  top: attr(),
  width: attr(),

  toStringExtension: function(){
    return this.get('description');
  }
});

Pd.Markup.reopen({
  selected: false,
  markupStyle: null
});

Pd.MarkupStyle = DS.Model.extend({
  name: attr(),
  color: attr(),
  border_style:attr()
});
