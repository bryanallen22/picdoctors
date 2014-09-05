// Just in case you're wondering, this uses whatever controller called him,
// currently since it's only used once, it's the pic controller (because
// the picS (note the s) controller has an itemController="pic"
Pd.EditablePicView = Ember.View.extend({
  templateName: '_pic_visual',

  picSpan: function(){
    return this.$().find('.markup_pic_container');
  }.property('pic'),

  newMarkup: null,
  newMarkupStartX: null,
  newMarkupStartY: null,

  mouseDown: function(e){
    if(e.which !== 1) return false;

    if(this.get('drawing')) { 
      this.finishMarkup(e);
      return;
    }

    this.set('drawing', true);
    var img = this.get('picSpan'),
        offset = img.offset(),
        controller = this.get('controller'),
        initialSize = 10;

    this.fixPageEventOffset(e, img, offset);

    /* The -6 magic here is:
     *       4px  (border width on one side
     *     + 2px  (half the border width on the other side
     *     = 6px
     *  This leaves us square in the middle of the lower right
     *  corner of our initial div size */
    var displayLeft = e.pageX - offset.left - initialSize - 6;
    var displayTop = e.pageY - offset.top - initialSize - 6;

    var newMarkup = controller.createMarkup();
    
    controller.deselectAllMarkups();

    newMarkup.setProperties({
      left:             displayLeft,
      top:              displayTop,
      height:           initialSize,
      width:            initialSize,
      selected:         true
    });

    this.set('newMarkup', newMarkup);
    this.setProperties({'newMarkupStartX': displayLeft, 'newMarkupStartY': displayTop});
  },

  mouseMove: function(e){
    if(!this.get('drawing')) return;

    //Ember.run.throttle(this, this.move, e, 15);
    this.move(e);
  },

  move: function(e){

    var img = this.get('picSpan'),
    img_offset = img.offset(),
    newMarkup = this.get('newMarkup');

    this.fixPageEventOffset(e, img, img_offset);


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

    newMarkup.setProperties( {
      left: left,
      top: top, 
      width: width, 
      height: height 
    });

  },

  fixPageEventOffset: function(e, img, img_offset){
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
        picController = this.get('controller'),
        x = e.pageX - img_offset.left,
        y = e.pageY - img_offset.top,
        xSize = Math.abs(x - this.get('newMarkupStartX')),
        ySize = Math.abs(y - this.get('newMarkupStartY')),
        minimum_size = 25;

    picController.selectAllMarkups();
    // If the markup is too small, get rid of it
    if( xSize < minimum_size ||  ySize < minimum_size ) {
      newMarkup.deleteRecord();
      return;
    }

    newMarkup.save().then(function(){
      Pd.Logger.timestamp('Saved new markup: ' + newMarkup.get('id'), 5); 
    },
    function(){
      Pd.Logger.timestamp('Failed to Save new markup!!!!!', 4); 
    });
  }

});

