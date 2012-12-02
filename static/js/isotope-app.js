// Give numbers to groups
var nextGroupId = 1;
var ungroupedId = 100000; // Make sure that this matches the original group in html
var CSRF_TOKEN = $('input[name=csrfmiddlewaretoken]').attr('value');

// Border Groups module
var BorderGroups = (function ($) {
  var $isocontainer = $('#isocontainer');
  var my = {};
  var borders = {};

  /* This needs to match the css padding for #isocontainer */
  var padding = 10;

  function _dumpBorders( borders ) {
    for( var groupId in borders) {
      console.log("borders[" + groupId.toString() + "]:")
      for( var key in borders[groupId]) {
        console.log("  " + key + " : " + borders[groupId][key])
      }
    }
  }

  function _drawBorders() {
    //_dumpBorders(borders);
        
    // Get rid of all existing borders
    $(".group_border").remove();

    for( var groupId in borders)
    {
      if( groupId < ungroupedId )
      {
        var border = $("<div id='border" + groupId.toString() + "' class='group_border' >");
        border.width(  borders[groupId]['width'] );
        border.height( borders[groupId]['height'] );
        border.css({ left: (borders[groupId]['x']+padding),
                      top: (borders[groupId]['y']+padding) });
        border.attr("group_id", groupId.toString());
        border.appendTo($isocontainer);
      }
    }
  }
  
  my.start = function() {
    borders = {}
  }

  my.end = function() {
    _drawBorders();
    // borders reset in start()
  }

  my.addElement = function (groupId, x, y, width, height) {
    // Update existing
    if( groupId in borders )
    {
      borders[groupId]['x']      = Math.min( borders[groupId]['x'],      x );
      borders[groupId]['y']      = Math.min( borders[groupId]['y'],      y );
      borders[groupId]['width']  = Math.max( borders[groupId]['width'],
          (x + width - borders[groupId]['x']) );
      borders[groupId]['height'] = Math.max( borders[groupId]['height'], 
          (y + height - borders[groupId]['y']) );
    }
    else // Create new
    {
      borders[groupId] = { 'x' : x,
        'y' : y,
        'width' : width,
        'height' : height };
    }
  }
  
  return my;
}(jQuery) );


// categoryRows custom layout mode
$.extend( $.Isotope.prototype, {
  
  extraHeight : 260,

  _categoryRowsReset : function() {
    this.categoryRows = {
      x : 0,
      y : 0,
      height : 0,
      currentCategory : null
    };
  },

  _categoryRowsLayout : function( $elems ) {
    var instance = this,
        containerWidth = this.element.width(),
        sortBy = this.options.sortBy,
        props = this.categoryRows;

    BorderGroups.start();
    
    /* Decrease extra height once we get items -- we just
       need some space at the beginning */
    if($elems.size()) {
      this.extraHeight = 160;
    }

    $elems.each( function() {
      var $this = $(this),
          atomW = $this.outerWidth(true),
          atomH = $this.outerHeight(true),
          category = $.data( this, 'isotope-sort-data' )[ sortBy ],
          x, y;

      if ( category !== props.currentCategory ) {
        // new category, new row
        props.x = 0;
        //props.x = instance.options.categoryRows.gutterX;
        props.height += props.currentCategory ? instance.options.categoryRows.gutterY : 0;
        //props.height += instance.options.categoryRows.gutterY;
        props.y = props.height;
        props.currentCategory = category;
      } else if ( props.x !== 0 && atomW + props.x > containerWidth ) {
        // if this element cannot fit in the current row
        props.x = 0;
        //props.x = instance.options.categoryRows.gutterX;
        props.y = props.height;
      }
      
      BorderGroups.addElement(  $this.attr("group_id"),
                                 props.x,
                                 props.y,
                                 atomW,
                                 atomH );

        // position the atom
      instance._pushPosition( $this, props.x, props.y );

      props.height = Math.max( props.y + atomH, props.height );
      props.x += atomW;
    });

    BorderGroups.end();
  },

  _categoryRowsGetContainerSize : function () {
    /* We add some pixels at the bottom, so the person sees some
     * empty space into which they can add pictures */
    return { height : this.categoryRows.height + this.extraHeight };
  },

  _categoryRowsResizeChanged : function() {
    return true;
  }

});

/*
 * This guy is smart about maintaining the isotope state
 */
var IsoWrapper = (function($) {
  var my = {}
  var numItems = 0;
  var $isocontainer = $('#isocontainer');

  my.addItem = function(item)
  {
    
  }

  my.relayout = function () {
    $isocontainer.isotope('reLayout');
  }

  my.startIso = function()
  {
    // Start isotope
    $isocontainer.isotope({
      // options
      itemSelector : '.pic_container',
      layoutMode   : 'categoryRows',
      categoryRows : {
        gutterX : 10,
        gutterY : 10
      },
      getSortData : {
        category : function( $elem ) {
          return parseInt($elem.attr('group_id'));
        }
      },
      sortBy : 'category',
      resizesContainer : true
    });

    // The images are preloaded (server side), but they are left hidden
    // so they don't jump around after the JS has loaded. Now that we've
    // started isotope, let's unhide them
    var pics = $isocontainer.find(".pic_container")
    if(pics.length > 0) {
      $("#next").removeClass('disabled');
    }
    pics.show();
  }

  my.sendGroupInfo = function(method, group_id, uuids) {

    var json = JSON.stringify(
        {
          "group_id" : group_id,
          "uuids"    : uuids,
        }
    );

    //console.log(method + ":" + json);
    $.ajax({
      headers: {
        "X-CSRFToken":CSRF_TOKEN
      },
      type: method,
      url: '/group_pic_handler/',
      data: json,
      success : function(data, textStatus) {
        //console.log("I got data back from /group_pic_handler/ -- have a look:");
        //console.log(data);
        //console.log(textStatus);
      }
    });
  }

  /*
   * Look for groups with fully uploaded pictures
   */
  my.checkForCompleteGroup = function(group_id)
  {
    //console.log('checkForCompleteGroup: group_id=' + group_id);
    if(group_id < ungroupedId) {
      /* Okay, this element is in a group. We'll upload group info
       * if it's the last pic in it's group to finish */
      var group_done = true;
      var uuids = [];
      var group_pics = $(".pic_container[group_id=" + group_id + "]");
      group_pics.each( function() {
        var my_uuid = $(this).attr("uuid");
        //console.log('uuid: ' + my_uuid);
        if( my_uuid ) {
          uuids.push( my_uuid );
        }
        else {
          /* Doesn't have a uuid yet, so it hasn't been uploaded yet. */
          group_done = false;
        }
      });
      if(group_done) {
        my.sendGroupInfo("POST", group_id, uuids);
      }
    }
  }

  /*
   * This is called after the upload has completed, and we have even
   * downloaded the template again too
   */
  my.picDownloaded = function(el)
  {
    /* Do we need to upload group information? */
    var group_id = el.attr("group_id");
    my.checkForCompleteGroup(group_id);

    //console.log("This just finished download:");
    //console.log(el);
  }

  return my;
}(jQuery) );


/*
 * Event handlers get tied in here
 */
$(function(){
  /* Private variables */
  var $isocontainer = $('#isocontainer');
  var hide_info = false;

  /******************
   * Fixed Controls *
   ******************/
  $("#group").popover(
    {
      placement : "left",
      title     : "Need to combine images?",
      content   : "Do you want the best of multiple pictures combined? Click individual pictures to select them, and then click \"Group\"",
      trigger   : "hover",
    } );

  /* Group button */
  $('#group').click( function(evt) {

    if( $(this).text() == "Group" ) {
      var selected_pics = $('.pic_container.selected');
      selected_pics.each( function() {
        $(this).attr("group_id", nextGroupId.toString() );
      } );

      selected_pics.removeClass('selected');
      $isocontainer.isotope('updateSortData', selected_pics);
      $isocontainer.isotope( { sortBy : 'category' } );
      
      /* If this group has fully downloaded pics, the server needs
       * to be informed */
      IsoWrapper.checkForCompleteGroup(nextGroupId);

      nextGroupId++;
    }
    else { // "Ungroup"
      // .first() used, though we only ever expect 1 group to be selected
      var border = $(".group_border.selected").first();
      group_id = $(border).attr("group_id");
      var uuids = [];

      // Get rid of the border
      $(border).remove();

      // Ungroup individual elements that have the appropriate id
      var ungroup_pics = $(".pic_container[group_id=" + group_id + "]");
      ungroup_pics.attr("group_id", ungroupedId);
      ungroup_pics.each( function() {
        uuids.push( $(this).attr("uuid") );
      });

      $isocontainer.isotope('updateSortData', ungroup_pics);
      $isocontainer.isotope( { sortBy : 'category' } );

      /* So, to even get grouped in the first place, we have to
       * be fully downloaded. This means we should be able to
       * disband the group immediately */
      IsoWrapper.sendGroupInfo("DELETE", group_id, uuids);
    }
  });

  /*************************
   * Dynamic/'live' Events *
   *************************/

  // When someone clicks a pic, highlight it. I like mousedown
  // better than click, because it was too easy to highlight
  // a picture (browser select, not my select)
  $('.pic_container').live('click', function(evt) {
    if( (evt.which == 1 ) && ( $(this).find('.error').size() == 0 ) ){ // left click
      var groupId = $(this).attr("group_id");
      if( groupId < ungroupedId ) {
        // unselect all other groups...
        for(var i=1; i < nextGroupId; i++) {
          if(i != groupId) {
            $("#border" + i).removeClass('selected');
          }
        }
        // and all individual selected pictures
        $('.pic_container').each( function() {
          $(this).removeClass("selected");
        });

        // select/unselect this group
        $("#border" + groupId).toggleClass('selected');

        // if we have just selected a group, we change the 'group'
        // button to an 'ungroup' button
        if( $("#border" + groupId).hasClass('selected') ) {
          $("#group").text("Ungroup");
        }
        else {
          $("#group").text("Group");
        }
      }
      else {
        // ungrouped picture
        $(this).toggleClass('selected');

        // unselect all groups
        for(var i=1; i < nextGroupId; i++) {
          $("#border" + i).removeClass('selected');
        }

        // Any time we are dealing with an individual pic,
        // it's time for grouping
        $("#group").text("Group");
      }
    }
  });

  $('.pic_container').live('mouseenter', function(evt) {
    if($(this).attr("group_id") == ungroupedId) {
      $(this).find('.del_pic').show();
    }
  });

  $('.pic_container').live('mouseleave', function(evt) {
    if($(this).attr("group_id") == ungroupedId) {
      $(this).find('.del_pic').hide();
    }
  });

  $('.del_pic').live('click', function(evt) {
    // TODO -- send some ajax up to do delete on server
    var pic_container = $(this).parent().parent();
    var uuid = pic_container.attr("uuid");

    // Am I still uploading? If so, time to cancel
    // TODO -- Tie into _cancelHandler

    if(uuid) {
      var json = JSON.stringify( { "uuid" : uuid, } );

      $.ajax({
        headers: {
          "X-CSRFToken":CSRF_TOKEN
        },
        type: 'DELETE',
        url: '/delete_pic_handler/',
        data: json,
        success : function(data, textStatus) {
          //console.log("I got data back from /delete_pic_handler/ -- have a look:");
          //console.log(data);
          //console.log(textStatus);
        }
      });
    }

    // Client side removal
    $isocontainer.isotope('remove', pic_container);
    pic_container.remove();
    IsoWrapper.relayout();
  });
});

/*
 * Set nextGroupId to be 1 larger than the largest existing group.
 * This is used when the upload page has prepopulated pictures from
 * a previous use of the page
 */
var setNextGroupId = function() {
  var max = 0;
  $(".pic_container").each( function () {
    var myId = parseInt($(this).attr("group_id"));
    if( (myId > max) && (myId < ungroupedId) ) {
      max = myId;
    }
  });
  nextGroupId = max + 1;
  //console.log("nextGroupId set to " + nextGroupId);
}

// Have to wait for images to load or this doesn't work nicely
$(window).load(function() {
  IsoWrapper.startIso();
  setNextGroupId();
});

