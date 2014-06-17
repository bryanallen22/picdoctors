attr = DS.attr;
belongsTo = DS.belongsTo;

Pd.Role = DS.Model.extend({
  user: belongsTo('user'),
  name: attr()
});
