// Create a self-executing function that will pass in a
// window object wrapper in a jquery container as well as
// the jQuery short-cut.
//
// NOTE: This will change all future references to the
// "window" object made in this scope.
;(function( window, $ ){
 
  // When the DOM is ready, initialize the page.
  $(function(){
 
    // Get references to our dom elements.
    var container = $( "#photo-container" );
 
    // Get a reference to our image being tagged.
    var image = container.children( "img" );
 
    // Get our message object (which we will add to the
    // container).
    var message = $( "<div class='tag-message'></div>" );
 
    // I am the collection of tags added to this photo.
    var tags = $( [] );
 
    // I am the pending tag - I am the one currently being
    // drawn by the user.
    var pendingTag = null;
 
 
    // Resize the container to be the dimensions of the
    // image so that we don't have any mouse confusion.
    container.width( image.width() );
    container.height( image.height() );
 
    // Add the message to the contianer.
    container.append( message );
 
 
    // I get the contianer-local top / left coordiantes
    // of the current mouse position based on the given page-
    // level X,Y coordinates.
    var getLocalPosition = function( mouseX, mouseY ){
      // Get the current position of the container.
      var containerOffset = container.offset();
 
      // Adjust the client coordiates to acocunt for
      // the offset of the page and the position of the
      // container.
      var localPosition = {
        left: Math.floor(
          mouseX - containerOffset.left + window.scrollLeft()
        ),
        top: Math.floor(
          mouseY - containerOffset.top + window.scrollTop()
        )
      };
 
      // Return the local position of the mouse.
      return( localPosition );
    };
 
 
    // I add a pending tag at the given position and store it
    // as the global pending tag.
    var addPendingTag = function( mouseX, mouseY ){
      // Get the local position of the mouse.
      var localPosition = getLocalPosition( mouseX, mouseY );
 
      // Create the new tag.
      var tag = $( "<a class='tag selected-tag'><br /></a>" );
 
      // Set the absolute positon (within the container).
      tag.css({
        left: (localPosition.left + "px"),
        top: (localPosition.top + "px")
      });
 
      // Set the anchor points for the tag. This is the
      // point from which the drawing will be made
      // (regardless of technical position).
      tag.data({
        anchorLeft: localPosition.left,
        anchorTop: localPosition.top
      });
 
      // Set it as the pending tag.
      pendingTag = tag;
 
      // Add it to the container.
      container.append( pendingTag );
 
      // Return the new tag.
      return( pendingTag );
    };
 
 
    // I resize the pending tag based on the given mouse
    // position.
    var resizePendingTag = function( mouseX, mouseY ){
      // Get the local position of the mouse.
      var localPosition = getLocalPosition( mouseX, mouseY );
 
      // Get the current anchor position of the tag.
      var anchorLeft = pendingTag.data( "anchorLeft" );
      var anchorTop = pendingTag.data( "anchorTop" );
 
      // Get the height and width of the pending tag based
      // on its current position plus the position of the
      // mouse.We're going to allow bi-directional drawing.
      var width = Math.abs(
        (localPosition.left - anchorLeft)
      );
 
      var height = Math.abs(
        (localPosition.top - anchorTop)
      );
 
      // Set the dimensions of the tag.
      pendingTag.width( Math.max( width, 1 ) );
      pendingTag.height( Math.max( height, 1 ) );
 
      // Check to see if the mouse position is greater
      // than the original anchor position, the move the
      // tag (this will give us the bi-directional re-size
      // illusion).
 
      // Check left.
      if (localPosition.left < anchorLeft){
 
        // Move left.
        pendingTag.css( "left", (localPosition.left + "px") );
 
      }
 
      // Check top.
      if (localPosition.top < anchorTop){
 
        // Move up.
        pendingTag.css( "top", (localPosition.top + "px") );
 
      }
    };
 
 
    // I finalize the pending tag after the drawing has
    // stopped.
    var finalizePendingTag = function(){
      // Get the tag information from the user.
      var message = prompt( "Message:" );
 
      // Check to see if the message was returned.
      if (message){
 
        // Associate the message with the tag.
        pendingTag.data( "message", message );
 
        // Remove the active tag status.
        pendingTag.removeClass( "selected-tag" );
 
        // Remove the anchor data as it will not be used
        // again.
        pendingTag.removeData( "anchorLeft" );
        pendingTag.removeData( "anchorTop" );
 
        // Bind the mouse over event on this tag.
        pendingTag.bind(
          "mouseover.tag",
          onTagMouseOver
        );
 
        // Bind the mouse out event on this tag.
        pendingTag.bind(
          "mouseout.tag",
          onTagMouseOut
        );
 
        // Add this as one of the tags.
        tags = tags.add( pendingTag );
 
      } else {
 
        // No message was provided so remove the tag from
        // the container as it is of no use.
        pendingTag.remove();
 
      }
 
      // Clear the pending tag.
      pendingTag = null;
    };
 
 
    // I handle the mouse over event on the tags. We are using
    // this rather than a "live" style binding for performance.
    var onTagMouseOver = function( event ){
      // Check to see if there is a pending tag. If so, then
      // return out - we don't want to mess with that.
      if (pendingTag){
        return;
      }
 
      // Get the current tag.
      var tag = $( this );
 
      // Get teh current position of the tag.
      var tagPosition = tag.position();
 
      // Set the tag message.
      message.text( tag.data( "message" ) );
 
      // Position and show the message.
      message
        .css({
          left: (tagPosition.left + "px"),
          top: ((tagPosition.top + tag.outerHeight() + 4) + "px")
        })
        .show()
      ;
 
      // Make this the selected tag.
      tag.addClass( "selected-tag" );
 
      // Dim the other tags' opacity.
      tags.css( "opacity", .25 );
 
      // Show the current tag.
      tag.css( "opacity", 1 );
    };
 
 
    // I handle the mouse out event on the tags. We are
    // using this rather than a "live" style binding for
    // performance.
    var onTagMouseOut = function( event ){
      // Check to see if there is a pending tag. If so,
      // then return out - we don't want to mess with that.
      if (pendingTag){
        return;
      }
 
      // Get the current tag.
      var tag = $( this );
 
      // Hide the message.
      message.hide();
 
      // Make sure to deselected tag.
      tag.removeClass( "selected-tag" );
 
      // Show all the tags.
      tags.css( "opacity", 1 );
    };
 
 
    // -------------------------------------------------- //
    // -------------------------------------------------- //
 
 
    // Bind to the hover event on the container. When the user
    // hovers over the container, we want to show the tags.
    container.hover(
      function(){
        // Show the tags be removing the "hide" class.
        container.removeClass( "hide-tags" );
      },
      function(){
        // Hide the tags by adding the "hide" class.
        container.addClass( "hide-tags" );
      }
    );
 
 
    // Bind to the mouse down even on the container.
    container.mousedown(
      function( event ){
        // Check to see if the user currently has the CTRL
        // key held down. We only want to start drawing a
        // tag IF the CTRL key is down so the user doesn't
        // start tagging the photo accidentally.
        //if (event.ctrlKey){
 
          // The user is going to start drawing. Cancel
          // the default event to make sure the browser
          // does not try to select the IMG object.
          event.preventDefault();
 
          // Add the pending tag to the container.
          addPendingTag( event.clientX, event.clientY );
 
          // Now that we are drawing a tag, let's bind
          // the mousemove event to the container.
          container.bind(
            "mousemove.tag",
            function( event ){
              // Resize the pending tag.
              resizePendingTag(
                event.clientX,
                event.clientY
              );
            }
          );
 
          // Now that we have started drawing, we're
          // going to need a way to STOP drawing. If
          // the user mouses-up, then finalize drawing.
          container.bind(
            "mouseup.tag",
            function(){
              // Unbinde any mouse up and mouse move
              // events related to tagging.
              container.unbind( "mouseup.tag" );
              container.unbind( "mousemove.tag" );
 
              // Finalize the pending tag.
              finalizePendingTag();
            }
          );
 
        //} // event.ctrlKey
      }
    );
 
  });
 
})( jQuery( window ), jQuery );

