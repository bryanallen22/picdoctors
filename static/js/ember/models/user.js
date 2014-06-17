attr = DS.attr;
belongsTo = DS.belongsTo;
hasMany = DS.hasMany;

Pd.User = DS.Model.extend({
  nickname:    attr(),
  email:       attr(),
  isLoggedIn:  attr(),
  roles:       hasMany('role'),
  emailConfig: belongsTo('emailConfig', { async: true }),
  isDoctor: Ember.computed.filterBy('roles', 'name', 'doctor'),
  isUser: Ember.computed.filterBy('roles', 'name', 'user'),
});
