/*// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

  if( $('.faq').length > 0 ) {

    // If they click a question, fadeIn/fadeOut the answer 
    $('.question').click( function() {
      var answers = $(this).siblings('.answer');
      for(var i = 0; i < answers.length; i++) {
        var answer = $(answers[i]);
        if(answer.is(':visible')) {
          answer.hide();
        }
        else {
          answer.fadeIn(150);
        }
      }
    });

  }

});*/
