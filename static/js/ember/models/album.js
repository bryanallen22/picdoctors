attr = DS.attr;
belongsTo = DS.belongsTo;
hasMany = DS.hasMany;

Pd.Album = DS.Model.extend({
  groups: hasMany('group'),
  job: belongsTo('job'),
  finished: attr(),
  owner: attr(),
  doctor: attr()
});
