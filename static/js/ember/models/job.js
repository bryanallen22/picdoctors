attr = DS.attr;
belongsTo = DS.belongsTo;
hasMany = DS.hasMany;

Pd.Job= DS.Model.extend({
  status: attr(),

  isDoctorAccepted: Ember.computed.equal('status', 'doctor_acc')

});
