attr = DS.attr;
belongsTo = DS.belongsTo;
hasMany = DS.hasMany;

Pd.Comment = DS.Model.extend({
  comment: attr(),
  commentor: belongsTo('user')
});
