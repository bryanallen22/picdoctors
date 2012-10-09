
  function textAreaResize (text) {
    if(text.srcElement){
      //this is for when resize is called directly
      text = text.srcElement;
    }

    if(text.value == '') {
      text.style.height = '20px';
      return;
    }

    text.style.height = 'auto';
    text.style.height = text.scrollHeight+'px';
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

  var text = $('.autosize-textarea');
  
  text.each(function(){
    joinAutoSize(this);
  });
  
});
