attr = DS.attr;
belongsTo = DS.belongsTo;
hasMany = DS.hasMany;

Pd.User = DS.Model.extend({
  nickname:    attr(),
  email:       attr(),
  isLoggedIn:  attr(),
  roles:       hasMany('role'),
  isDoctor:    attr(),
  isUser:      attr(),
  emailConfig: belongsTo('emailConfig', { async: true }),
});
