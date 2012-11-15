

  function textAreaResize (text) {
    if(text.target){
      //for some reason chrome sends as event, ff sends the target item
      text = text.target;
    }

    var isDisabled = true;

    if($(text).attr('disabled')==undefined){
      isDisabled = false;
    }
    var min_height = 0;
    if($(text).attr('auto-minheight')!=undefined){
      min_height = parseInt($(text).attr('auto-minheight'));
    }

    if(text.value == '') {
      text.style.height = Math.max(20, min_height) + 'px';
      return;
    }

    text.style.height = 'auto';
    var adder = isDisabled ? -20 : 0;
    var total = text.scrollHeight+adder;

    total = Math.max(total, min_height);
    text.style.height = (total) +'px';
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

String.prototype.pluralize = function(count, plural)
{
    if (plural == null)
          plural = this + 's';

      return (count == 1 ? this : plural)
}


Number.prototype.padLeft = function(n,str){
      return Array(n-String(this).length+1).join(str||'0')+this;
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
