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
  doc_profile_page: function(){
    var nick = this.get('nickname'),
        base = location.protocol + '//' + location.host,
        url = base + '/doctor_profile/' + nick;
    return url;
  }.property()
});
