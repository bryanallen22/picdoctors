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


Pd.Resize = {

  textAreaResize: function(text) {
    // save scrol location so we can restore it
    var scrollTop = $('body').scrollTop();

    //for some reason chrome sends as event, ff sends the target item
    text = text.target || text;

    var isDisabled = true;

    if($(text).attr('disabled') === undefined){
      isDisabled = false;
    }
    var min_height = 0;
    if($(text).attr('auto-minheight') !== undefined){
      min_height = parseInt($(text).attr('auto-minheight'));
    }

    if(text.value === '') {
      text.style.height = Math.max(20, min_height) + 'px';
      return;
    }

    text.style.height = 'auto';
    var adder = isDisabled ? -20 : 0;
    var total = text.scrollHeight+adder;

    total = Math.max(total, min_height);
    text.style.height = (total) +'px';

    // restore scroll position
    $('body').scrollTop(scrollTop);
  },

  /* get already changed text */
  delayedResize : function() {
    var self = this;
    window.setTimeout(function(){ self.textAreaResize(self); }, 0);
  },

  //allow me to join items post page being loaded
  joinAutoSize: function(el){
    var self = this;
    $(el).on('change',  textAreaResize);
    $(el).on('cut',     delayedResize);
    $(el).on('paste',   delayedResize);
    $(el).on('drop',    delayedResize);
    $(el).on('keydown', delayedResize);

    // init the resize
    setTimeout(function(){ self.textAreaResize(el);}, 50);
  }

};
