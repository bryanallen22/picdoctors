attr = DS.attr;
belongsTo = DS.belongsTo;
hasMany = DS.hasMany;

Pd.User = DS.Model.extend({
  nickname:    attr(),
  email:       attr(),
  isLoggedIn:  attr(),
  roles:       hasMany('role'),
  emailConfig: belongsTo('emailConfig', { async: true }),
  stripe_user:   attr(),
  isDoctor:    Ember.computed.filterBy('roles', 'name', 'doctor'),
  isUser:      Ember.computed.filterBy('roles', 'name', 'user'),
});
