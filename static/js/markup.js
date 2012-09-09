// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){
  
  var markup_colors = [
    /* I don't like this, but I suck at javascript. Better way? */
    {'name':'Blue',             'value':'#049cdb', 'border-style':'solid'},
    {'name':'Green',            'value':'#46a546', 'border-style':'solid'},
    {'name':'Red',              'value':'#9d261d', 'border-style':'solid'},
    {'name':'Yellow',           'value':'#ffc40d', 'border-style':'solid'},
    {'name':'Dark blue',        'value':'#0064cd', 'border-style':'solid'},
    {'name':'Orange',           'value':'#f89406', 'border-style':'solid'},
    {'name':'Pink',             'value':'#c3325f', 'border-style':'solid'},
    {'name':'Purple',           'value':'#7a43b6', 'border-style':'solid'},
    {'name':'Dotted blue',      'value':'#049cdb', 'border-style':'dotted'},
    {'name':'Dotted green',     'value':'#46a546', 'border-style':'dotted'},
    {'name':'Dotted red',       'value':'#9d261d', 'border-style':'dotted'},
    {'name':'Dotted yellow',    'value':'#ffc40d', 'border-style':'dotted'},
    {'name':'Dotted dark blue', 'value':'#0064cd', 'border-style':'dotted'},
    {'name':'Dotted orange',    'value':'#f89406', 'border-style':'dotted'},
    {'name':'Dotted pink',      'value':'#c3325f', 'border-style':'dotted'},
    {'name':'Dotted purple',    'value':'#7a43b6', 'border-style':'dotted'},
    {'name':'Dashed blue',      'value':'#049cdb', 'border-style':'dashed'},
    {'name':'Dashed green',     'value':'#46a546', 'border-style':'dashed'},
    {'name':'Dashed red',       'value':'#9d261d', 'border-style':'dashed'},
    {'name':'Dashed yellow',    'value':'#ffc40d', 'border-style':'dashed'},
    {'name':'Dashed dark blue', 'value':'#0064cd', 'border-style':'dashed'},
    {'name':'Dashed orange',    'value':'#f89406', 'border-style':'dashed'},
    {'name':'Dashed pink',      'value':'#c3325f', 'border-style':'dashed'},
    {'name':'Dashed purple',    'value':'#7a43b6', 'border-style':'dashed'},
  ];
  var color_index = 0;
  var total_index = 0;
  var minimum_width = 25;

  // Our basic **Markup** model has 'left', 'top', 'width', 'height',
  // 'color', and 'description' attributes.
  var Markup = Backbone.Model.extend({

    // Default attributes for the todo item.
    defaults: function() {
      return {
        left:         0,
        top:          0,
        width:        0,
        height:       0,
        color:        '#ffffff',
        color_name:   '',
        description:  '',
        border_style: '',

        // Server shouldn't care about this one:
        hidden:       false,
        desc_el_id:   '',
      };
    },
    
    initialize : function() {
      //console.log("I'm making me a Markup model!");
      //console.log(this);
    },

    clear: function() {
      this.destroy();
    },

    // TODO: get rid of this so the model is actually saved
    sync: function () {
      console.log("sync:", this.attributes);
      return false;
    },

  });

  // Markup Collection
  // ---------------

  // A collection of Markup elements
  var MarkupList = Backbone.Collection.extend({

    // Reference to this collection's model.
    model: Markup,

    // Url base
    //url: '/markups/',
    
    initialize: function() {
      this.container = null; // Will be set to our .markup_pic_container element
      this.bind('add', this.addOne, this);
    },

    addOne: function(markup) {
      var view = new MarkupView( { model: markup } );
      var desc = new MarkupDesc( { model: markup } );
      this.container.append( view.render().el );
      this.container.closest('.markup_outer')
        .find('.markup_desc_container').append( desc.render().el );
    },

    showJustOne: function( showed ) {
      this.each( function( el ) { 
        if( el != showed.model ) {
          el.set( { hidden : true } );
        }
      });
    },

    showAll: function() {
      this.each( function( el ) { 
        if( el.get('hidden') ) {
          el.set( { hidden : false } );
        }
      });
    }

  });

  // The DOM element for a markup item...
  var MarkupView = Backbone.View.extend({

    //... is a div tag.
    tagName:  "div",

    className: "markup",

    // Cache the template function for a single item.
    template:      _.template( $('#markup-template-styleattr').html().trim() ),

    redX_template: _.template( $('#markup-template-redx').html().trim() ),

    // The DOM events specific to an item.
    events: {
      // This event needs to be mousedown instead of click, because otherwise
      // when we depress the mouse, we'll find ourselves in the middle of 
      // creating a new markup rather than deleting this one. (mousedown 
      // is caught by the markup_pic_container)
      "mousedown .markup-redx" : "deleteMarkup",
    },

    // The MarkupView listens for changes to its model, re-rendering.
    // Since there's a one-to-one correspondence between a **Markup** 
    // and a **MarkupView** in this app, we set a direct reference on 
    // the model for convenience.
    initialize: function() {
      //console.log("And, in the morning, I'm making MarkupView(s)!");
      //console.log(this);
      this.model.bind('change', this.render, this);
      this.model.bind('destroy', this.remove, this);
    },

    // Re-render the titles of the todo item.
    render: function() {
      console.log('render: ' + this.model.get('desc_el_id'));
      //this.$el.attr('style', this.template(this.model.toJSON()));
      this.$el.attr('style', this.template(
            {
              left:          this.model.get('left')   + 'px',
              top:           this.model.get('top')    + 'px',
              width:         this.model.get('width')  + 'px',
              height:        this.model.get('height') + 'px',
              color:         this.model.get('color'),
              border_style:  this.model.get('border_style'),
            }
      ));

      // Doesn't display well on really small widths
      this.$el.html( this.redX_template( {} ) );
      this.$el.find('.markup-redx').css('left', this.model.get('width')-20 );

      if( this.model.get('hidden') ) {
        this.$el.css('opacity', 0.3);
        this.$el.css('z-index', 100);
      }
      return this;
    },

    deleteMarkup: function() {
      this.$el.fadeOut( function () {
        this.model.destroy();
      } );
    }

  });

  // The DOM element for a markup item...
  var MarkupDesc = Backbone.View.extend({

    //... is a div tag.
    tagName:  "div",

    className: "markup_desc",

    template:      _.template( $('#markup-template-desc').html() ),

    // The DOM events specific to an item.
    events: {
      //"click .toggle"   : "toggleDone",
      "focusin   .desc" : "focusIn",
      "focusout  .desc" : "focusOut",
      "mousedown .desc" : "mouseDown",
      "keyup   .desc"   : "keyUp",
    },

    // The MarkupView listens for changes to its model, re-rendering.
    // Since there's a one-to-one correspondence between a **Markup** 
    // and a **MarkupView** in this app, we set a direct reference on 
    // the model for convenience.
    initialize: function() {
      //console.log("MarkupDesc initializationz!");
      //console.log(this);
      this.model.bind('change', this.render, this);
      this.model.bind('destroy', this.remove, this);
      
    },

    // Re-render the titles of the todo item.
    render: function() {
      //this.$el.attr('style', this.template(this.model.toJSON()));
      this.$el.html( this.template(
          {
            color         : this.model.get('color'),
            color_name    : this.model.get('color_name') + ' area instructions:',
            border_style  : this.model.get('border_style'),
            desc          : this.model.get('description'),
            desc_el_id    : this.model.get('desc_el_id'),
          }
      ));

      return this;
    },

    focusIn : function() {
      console.log("focusIn");
      this.$el.closest('.markup_outer').data('markup_list')
        .showJustOne( this );
    },

    focusOut : function() {
      //Save the description to the model on focus out
      //I felt guilty and added an element id 
      console.log('save description');
      var el_id = this.model.get('desc_el_id');
      this.model.set('description', $('#' + el_id).val());
      
      console.log("focusOut");
      this.$el.closest('.markup_outer').data('markup_list')
        .showAll();
    },

    keyUp : function()
    {
      console.log("keyUp");
      //if you attempt to save description here it causes a render
      //and focus loss, jack ass
    },

    mouseDown: function()
    {
      var el_id =  this.model.get('desc_el_id');
      console.log('mouseDown for ' + el_id );
      var el = $('#' + el_id);
      setTimeout(function(){focusFix(el_id)},10); 
    },

  });

  function focusFix(el_id)
  {
    console.log('fake focus');
    var el = $('#' + el_id);
    var dom_el = el[0];
    el.focus();       
    dom_el.value = dom_el.value;
    
  }

  // The Application
  // ---------------

  // Our overall **AppView** is the top-level piece of UI.
  var AppView = Backbone.View.extend({

    // Our template for the line of statistics at the bottom of the app.
    //statsTemplate: _.template($('#stats-template').html()),

    el: $("#markup_app"),

    // Delegated events for creating new items, and clearing completed ones.
    events: {
      //"keypress #new-todo":  "createOnEnter",
      "mousedown  .markup_pic_container" : "createMarkup",
      "mousemove  .markup_pic_container" : "resizeMarkup",
      "mouseup    .markup_pic_container" : "finishMarkup",
      //"mouseleave .markup_pic_container" : "finishMarkup",
    },

    // At initialization we bind to the relevant events on the `Todos`
    // collection, when items are added or changed. Kick things off by
    // loading any preexisting todos that might be saved in *localStorage*.
    initialize: function() {

      //console.log("AppView init");

      $(".markup_outer").each( function() {
        // Create a MarkupList on each element
        var markup_list = new MarkupList;
        markup_list.container = $(this).find(".markup_pic_container");
        $(this).data("markup_list", markup_list);

      });

    },

    // Re-rendering the App just means refreshing the statistics -- the rest
    // of the app doesn't change.
    render: function() {
        console.log('render app view');
    },

    createMarkup: function(e) {
      if(e.which == 1) { // left click
        var initial_size = 10;
        /* This seems like a lot of work, but e.target seems a little bit
         * unpredictable, so I'm dancing around to ensure that I always end
         * up at my desired .markup_pic_container element */
        this.pic_container = $(e.target).closest('.markup_outer')
          .find(".markup_pic_container");
        var left = e.pageX - this.pic_container.offset().left - initial_size;
        var top = e.pageY - this.pic_container.offset().top - initial_size;

        /* e.currentTarget would be better, but apparently Redmond doesn't
         * like it. See here: http://www.quirksmode.org/js/events_order.html */
        this.cur_markup = this.pic_container.parent().data("markup_list").create(
            {
              /* The -6 magic here is:
               *       4px  (border width on one side
               *     + 2px  (half the border width on the other side
               *     = 6px
               *  This leaves us square in the middle of the lower right
               *  corner of our initial div size */
              left:          (left-6),
              top:           (top -6),
              height:        initial_size,
              width:         initial_size,
              color:         markup_colors[color_index]['value'],
              color_name:    markup_colors[color_index]['name'],
              border_style:  markup_colors[color_index]['border-style'],
              desc_el_id:    'desc_el_id_' + total_index++,
            }
        );

        if( ++color_index >= markup_colors.length ) {
          color_index = 0;
        }

        this.cur_markup_startX = (left-6);
        this.cur_markup_startY = (top-6);
      }
    },

    resizeMarkup: function(e) {
      // Only care if we're in the middle of a move and they the left mouse is pressed
      if( this.cur_markup && e.which == 1) {
        var img = this.pic_container;
        var img_offset = img.offset();


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
        var x1 = e.pageX - this.pic_container.offset().left;
        var y1 = e.pageY - this.pic_container.offset().top;
        var x2 = this.cur_markup_startX;
        var y2 = this.cur_markup_startY;

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

        this.cur_markup.set( { left: left, top: top, width: width, height: height } );
      }
    },

    finishMarkup: function(e) {
      var x = e.pageX - this.pic_container.offset().left;
      var y = e.pageY - this.pic_container.offset().top;

      // TODO: If width < minimum_width, just get rid of this tiny thing.
      if( (Math.abs(x - this.cur_markup_startX) < minimum_width) ||
          (Math.abs(y - this.cur_markup_startY) < minimum_width) ) {
          console.log("Too small - destroy it now!");
          this.cur_markup.destroy();
          // Let's redo that color -- decrement back
          if( --color_index < 0 ) {
            color_index = markup_colors.length;
          }
      }

      this.cur_markup = null;
      this.cur_markup_startX = null;
      this.cur_markup_startY = null;
      this.pic_container = null;
    },

  });

  // Finally, we kick things off by creating the **App**.
  var App = new AppView;

});
