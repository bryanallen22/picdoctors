attr = DS.attr;
belongsTo = DS.belongsTo;
hasMany = DS.hasMany;

Pd.User = DS.Model.extend({
  nickname:    attr(),
  email:       attr(),
  isLoggedIn:  attr(),
  isDoctor:    attr(),
  isUser:      attr(),
  emailConfig: belongsTo('emailConfig', { async: true }),
});
