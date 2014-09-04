Pd.SubmitTextFieldView = Ember.TextField.extend({
  insertNewline: function() {
    this.sendAction('enter');
  }
});
