//Load these things once the DOM is ready
$(function(){

  function go_previous_next(e) { 
    if(e.originalTarget && e.originalTarget.type=="textarea") 
      return;
    if(e.srcElement && e.srcElement.nodeName=="TEXTAREA") 
      return;
    var keynum; 
    keynum = e.keyCode;
    if(keynum==37){
      var go_where = $('#previous').attr('href');
      window.location = go_where;
    }
    if(keynum==39){
      var go_where = $('#next').attr('href');
      window.location = go_where;
    } 
  } 
  if (document.addEventListener){
    document.addEventListener('keypress', go_previous_next, false);
    document.addEventListener('keyup', go_previous_next, false);
  }  
  else if (document.attachEvent){ 
    window.document.attachEvent('onkeyup', function(e){go_previous_next(e);},false );
  } 

  var scrollTop = $("#buttons").offset().top;
  // Lame hack to slide buttons down. 'position:fixed' would be much nicer,
  // but it hates me on very narrow windows.
  $(window).scroll(function(event) {
    var loc = $(this).scrollTop() + scrollTop;
    $("#buttons").offset( { 'top' : loc } );
  });

});
