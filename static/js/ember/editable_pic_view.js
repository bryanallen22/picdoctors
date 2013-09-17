Pd.EditablePicView = Ember.View.extend({
  templateName: 'pic_span',
didInsertElement: function() {
  this._super();
},

picsMarkups: function(){
  return this.get('content.markups');
}.property('content.markups'),

picSpan: function(){
  return this.$().find('.markup_pic_container');
}.property('content'),

newMarkup: null,
newMarkupStartX: null,
newMarkupStartY: null,

mouseDown: function(e){
  this.get('picsMarkups').forEach(function(markup){
    console.log(markup.get('pic'));
  });
  if(e.which === 1){
    this.set('drawing', true);
    var offset = this.get('picSpan').offset(),
        store = this.get('controller.store'),
        initialSize = 10;

    /* The -6 magic here is:
     *       4px  (border width on one side
     *     + 2px  (half the border width on the other side
     *     = 6px
     *  This leaves us square in the middle of the lower right
     *  corner of our initial div size */
    var displayLeft = e.pageX - offset.left - initialSize - 6;
    var displayTop = e.pageY - offset.top - initialSize - 6;

    var newMarkup = store.createRecord(Pd.Markup, {
      left:             displayLeft,
        top:              displayTop,
        height:           initialSize,
        width:            initialSize,
        pic:              this.get('content')
    });


    this.set('newMarkup', newMarkup);
    this.set('newMarkupStartX', displayLeft);
    this.set('newMarkupStartY', displayTop);

    this.get('picsMarkups').pushObject(newMarkup);
  }

},

  mouseMove: function(e){
    if(!this.get('drawing')) return;

    var img = this.get('picSpan'),
        img_offset = img.offset(),
        newMarkup = this.get('newMarkup');


    /*
       console.log( "limits: X:[", img_offset.left, "..",
       img_offset.left + img.width(), "]   Y:[",
       img_offset.top, "..",
       img_offset.top  + img.height(), "]" );
       */

    /* Sometimes I get events that are outside of the div. Me no likey. Fix
     * that here.
     *
     * I'm modifying the e.pageXY attributes directly. How evil am I? */
    if( e.pageX < img_offset.left ) {
      e.pageX = img_offset.left;
    }
    if( e.pageX > img_offset.left + img.width() - 6 ) {
      e.pageX = img_offset.left + img.width() - 6;
    }
    if( e.pageY < img_offset.top ) {
      e.pageY = img_offset.top;
    }
    if( e.pageY > img_offset.top + img.height() - 6 ) {
      e.pageY = img_offset.top + img.height() - 6;
    }

    /* Okay, time to actually resize stuff */
    var x1 = e.pageX - img_offset.left;
    var y1 = e.pageY - img_offset.top;
    var x2 = this.get('newMarkupStartX');
    var y2 = this.get('newMarkupStartY');

    /* We've got <x1, y1> and <x2, y2>. Depending on which way they are
     * dragging,(top left to bottom right, top right to bottom left, 
     * whatever) one of the two will be the new 'left'/'top' coordinate,
     * and the other will be used to get the width and height */
    var left, top, width, height;
    if( x1 < x2 ) {
      left = x1;
      width = x2 - x1;
    } else {
      left = x2;
      width = x1 - x2;
    }

    if( y1 < y2 ) {
      top = y1;
      height = y2 - y1;
    } else {
      top = y2;
      height = y1 - y2;
    }

    newMarkup.setProperties( { left: left, top: top, width: width, height: height } );



  },

  mouseUp: function(e){
    this.finishMarkup(e);
  },

  mouseLeave: function(e){
    this.finishMarkup(e);
  },

  finishMarkup: function(e){

    if(!this.get('drawing')) return;

    this.set('drawing', false);

    var img = this.get('picSpan'),
        img_offset = img.offset(),
        newMarkup = this.get('newMarkup'),
        store = this.get('controller.store'),
        x = e.pageX - img_offset.left,
        y = e.pageY - img_offset.top,
        minimum_size = 25;

    // If the markup is too small, get rid of it
    if( (Math.abs(x - this.get('newMarkupStartX')) < minimum_size) ||
        (Math.abs(y - this.get('newMarkupStartY')) < minimum_size) ) {
       newMarkup.destroy();
       this.get('picsMarkups').removeObject(newMarkup);
       return;
    }
    var pic = newMarkup.get('pic');
    //weird hackary for a sec while I figure out ember data.
    newMarkup.set('pic', pic.get('id'));
    // note it reloads the model based on the results
  // so I need to return the model back so it reloads correctly!
    newMarkup.save().then(function(){
      newMarkup.set('pic', pic);
    });


  }

});

