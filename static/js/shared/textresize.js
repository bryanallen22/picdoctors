TextAreaResize = {

  // resize a textarea
  textAreaResize: function(text) {

    // save scroll location so we can restore it
    var scrollTop = $('body').scrollTop(),

    //for some reason chrome sends as event, ff sends the target item
    text = text.target || text;

    var jText = $(text);
    jText.css('overflowY', 'hidden');

    var isDisabled = true;

    if(jText.attr('disabled') === undefined){
      isDisabled = false;
    }
    var min_height = 0;
    if(jText.attr('auto-minheight') !== undefined){
      min_height = parseInt(jText.attr('auto-minheight'));
    }


    if(text.value === '') {
      text.style.height = Math.max(20, min_height) + 'px';
      return;
    }

    text.style.height = 'auto';
    var adder = isDisabled ? -10 : 0;
    var total = text.scrollHeight+adder;

    total = Math.max(total, min_height);
    text.style.height = (total) +'px';

    // restore scroll position
    $('body').scrollTop(scrollTop);
  },

  /* get already changed text */
  delayedResize : function(ev) {
    var self = ev.data.self;
    window.setTimeout(function(){ self.textAreaResize(ev); }, 0);
  },

  //allow me to join items post page being loaded
  joinAutoSize: function(el){
    var self = this;
    $(el).on('change',  this.textAreaResize);
    $(el).on('cut',    {self:this}, this.delayedResize);
    $(el).on('paste',  {self:this}, this.delayedResize);
    $(el).on('drop',   {self:this}, this.delayedResize);
    $(el).on('keydown', {self:this}, this.delayedResize);

    // init the resize
    setTimeout(function(){ self.textAreaResize(el);}, 50);
  }

};

$(function(){
  // set up autosize-textareas
  var text = $('.autosize-textarea');
  
  text.each(function(){
    TextAreaResize.joinAutoSize(this);
  });

});
