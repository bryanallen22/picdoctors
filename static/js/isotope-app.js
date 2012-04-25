// Give numbers to groups
var nextGroup   = 1;
var ungroupedId = 10000; // Make sure that this matches the original group in html

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
        border.appendTo($isocontainer);
        border.width(  borders[groupId]['width'] );
        border.height( borders[groupId]['height'] );
        border.css({ left: (borders[groupId]['x']+padding),
        top:  (borders[groupId]['y']+padding) });
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

    $elems.each( function() {
      var $this = $(this),
          atomW = $this.outerWidth(true),
          atomH = $this.outerHeight(true),
          category = $.data( this, 'isotope-sort-data' )[ sortBy ],
          x, y;
      
      //console.log("atomW=" + atomW + ", atomH=" + atomH);
      
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
      
      BorderGroups.addElement(  $this.attr("data-category"),
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
    /* We add 160 pixels at the bottom, so the person sees some
     * empty space into which they can add pictures */
    return { height : this.categoryRows.height + 160 };
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

  my.start_iso = function()
  {
    var qty = $isocontainer.find(".pic_container").size();

    //console.log("start_iso: top");
    //if(qty == 0)
    //{
    //  console.log("start_iso: qty=0");
    //  return;
    //}
    //else
    //{
    //  // Get rid of info
    //  $isocontainer.find(".instructions").remove();
    //}

    //console.log("start_iso: about to start iso");
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
          return parseInt($elem.attr('data-category'));
        }
      },
      sortBy : 'category',
      resizesContainer : true
    });

    //console.log("start_iso: finished starting isotope");
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

  //console.log("about to start_iso");
  /* If you prepopulate pictures, this is not a good way
   * to start Isotope - you should do it in window.ready(),
   * after the pictures have loaded. Since there are never
   * any pictures in here on page load, we put it here */
  //IsoWrapper.start_iso();
  //console.log("just ran start_iso");


  /******************
   * Fixed Controls *
   ******************/

  /* Toggle Info button */
  $('#toggle_hide_info').click( function(evt) {
    evt.preventDefault();
    if(hide_info) {
      $(".pic_info").hide('fast', IsoWrapper.relayout);
    }
    else {
      $(".pic_info").show('fast', IsoWrapper.relayout);
    }
    hide_info = !hide_info;
  });

  /* Group button */
  $('#group').click( function(evt) {
    evt.preventDefault();

    var selected_items = $('.selected');
    selected_items.each( function() {
      $(this).attr("data-category", nextGroup.toString() );
    } );

    selected_items.removeClass('selected');
    $isocontainer.isotope('updateSortData', selected_items);
    $isocontainer.isotope( { sortBy : 'category' } );

    nextGroup++;
  });

  /* Relayout button */ 
  $('#relayout').click( IsoWrapper.relayout );



  /*************************
   * Dynamic/'live' Events *
   *************************/

  // When someone clicks a pic, highlight it. I like mousedown
  // better than click, because it was too easy to highlight
  // a picture (browser select, not my select)
  $('.pic_container').live('click', function(evt) {
    if( (evt.which == 1 ) && ( $(this).find('.error').size() == 0 ) ){ // left click
      $(this).toggleClass('selected');
    }
  });

  $('.pic_container').live('mouseenter', function(evt) {
    $(this).find('.del_pic').show();
  });

  $('.pic_container').live('mouseleave', function(evt) {
    $(this).find('.del_pic').hide();
  });

  $('.del_pic').live('click', function(evt) {
    // TODO -- send some ajax up to do delete on server
    var pic_container = $(this).parent().parent();
    $isocontainer.isotope('remove', pic_container);
    $(this).parent().remove();
    IsoWrapper.relayout();
  });
});

// Have to wait for images to load or this doesn't work nicely
$(window).load(function() {
  IsoWrapper.start_iso();
});

