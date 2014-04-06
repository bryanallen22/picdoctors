attr = DS.attr;
belongsTo = DS.belongsTo;
hasMany = DS.hasMany;

Pd.Message = DS.Model.extend({
  message: attr(),
  commentor: attr(),
  commentor_id:attr(),
  created: attr(),
  is_owner: attr(),
  group: belongsTo('group'),
  job: belongsTo('job')
});
