

  function textAreaResize (text) {
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
    // delay the resize...
    // I can't reproduce this in dev, so modify and push to prod
    setTimeout(function(){ textAreaResize(el);}, 50);
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

});
