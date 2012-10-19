

  function textAreaResize (text) {
    if(text.target){
      //for some reason chrome sends as event, ff sends the target item
      text = text.target;
    }

    var isDisabled = true;

    if($(text).attr('disabled')==undefined){
      isDisabled = false;
    }

    if(text.value == '') {
      text.style.height = '20px';
      return;
    }

    text.style.height = 'auto';
    var adder = isDisabled ? -20 : 0;
    text.style.height = (text.scrollHeight+adder) +'px';
  }
  /* get already changed text */
  function delayedResize () {
    el = this;
    window.setTimeout(function(){ textAreaResize(el); }, 0);
  }

  //allow me to join items post page being loaded
  function joinAutoSize(el){
    $(el).on('change',  textAreaResize);
    $(el).on('cut',     delayedResize);
    $(el).on('paste',   delayedResize);
    $(el).on('drop',    delayedResize);
    $(el).on('keydown', delayedResize);
    textAreaResize(el);
  }

$(function(){
  // set up autosize-textareas
  var text = $('.autosize-textarea');
  
  text.each(function(){
    joinAutoSize(this);
  });

  //start up any carousels
  $('.carousel').carousel('next');
  $('.carousel').carousel();
  
});
