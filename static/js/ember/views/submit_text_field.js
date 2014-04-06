Pd.SubmitTextField = Ember.TextField.extend({
  insertNewline: function() {
    this.sendAction('enter');
  }
});
