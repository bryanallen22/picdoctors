attr = DS.attr;
belongsTo = DS.belongsTo;
hasMany = DS.hasMany;

Pd.Album = DS.Model.extend({
  groups: hasMany('group'),
  finished: attr(),
  owner: attr(),
  doctor: attr()
});
