// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

  var prefetchImage = function(url) {
    var im = new Image();
    im.src = url;
  }

  var getUrlFromBackground = function(el) {
    var background = $(el).css('background');
    if(background) {
      var urlregex = /url\((.*)\)/;
      var results = urlregex.exec(background);
      if(results && results.length >= 2) {
        return results[1];
      }
    }
  }

  $('#myCarousel').carousel({
      interval: 8000,
      pause: null, /* Don't pause when they hover over it */
  }).on('slide', function (e) {
    /* We're already sliding to the image at e.relatedTarget. (Hopefully
     * that image is already prefetched!) Let's prefetch the *following*
     * image so that the next transition is smooth!
     *   - The first image is part of the page download
     *   - The second image is fetched by hand -- see below
     *   - This code here will fetch the 3rd and beyond images
     */
    var nextImageEl = $(e.relatedTarget).next().find('.photo');
    prefetchImage(getUrlFromBackground(nextImageEl));

    //var nextImageCss = $(e.relatedTarget).next().find('.photo').css('background');
    //if(nextImageCss) {
    //  /* Extract the url from the background */
    //  var urlregex = /url\((.*)\)/;
    //  var results = urlregex.exec(nextImageCss);
    //  if(results.length >= 2) {
    //    prefetchImage(results[1]);
    //  }
    //}
  });

  var secondPic = $('.active.item').next().find('.photo');
  var url = getUrlFromBackground(secondPic);
  prefetchImage(url);

});
