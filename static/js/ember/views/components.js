Pd.AutoGrowTextArea = Ember.TextArea.extend({
  didInsertElement: function() {
    Pd.Resize.joinAutoSize(this.$()[0]);
    this._super();
  },
  focusIn: function(){
    var focusIn = this.get('focusInEvent'),
    delegate = this.get('eventDelegate');
    if(focusIn){
      delegate.send(focusIn);
    }
  },
  focusOut: function(){
    var focusOut = this.get('focusOutEvent'),
    delegate = this.get('eventDelegate');
    if(focusOut){
      delegate.send(focusOut);
    }
  },
  keyUp: function(){
    var keyUp = this.get('keyUpEvent'),
    delegate = this.get('eventDelegate');
    if(keyUp){
      delegate.send(keyUp);
    }
  },
});
