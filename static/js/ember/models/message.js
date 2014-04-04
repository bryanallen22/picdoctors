attr = DS.attr;
belongsTo = DS.belongsTo;
hasMany = DS.hasMany;

Pd.Message = DS.Model.extend({
  message: attr(),
  commentor: attr()
});
