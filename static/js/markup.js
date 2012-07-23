// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){
  
  var markup_colors = [
    /* I don't like this, but I suck at javascript. Better way? */
    { 'name' : 'Blue',      'value' : '#049cdb' },
    { 'name' : 'Green',     'value' : '#46a546' },
    { 'name' : 'Red',       'value' : '#9d261d' },
    { 'name' : 'Yellow',    'value' : '#ffc40d' },
    { 'name' : 'Dark blue', 'value' : '#0064cd' },
    { 'name' : 'Orange',    'value' : '#f89406' },
    { 'name' : 'Pink',      'value' : '#c3325f' },
    { 'name' : 'Purple',    'value' : '#7a43b6' },
  ];
  var color_index = 0;
  var minimum_width = 30;

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
      var desc   = new MarkupDesc( { model: markup } );
      this.container.append( view.render().el );
      this.container.parentsUntil("#markup_app").last().find('.markup_desc_container').append( desc.render().el );
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
      //"click .toggle"   : "toggleDone",
      "click .markup-redx" : "deleteMarkup",
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
      //this.$el.attr('style', this.template(this.model.toJSON()));
      this.$el.attr('style', this.template(
            {
              left:   this.model.get('left')   + 'px',
              top:    this.model.get('top')    + 'px',
              width:  this.model.get('width')  + 'px',
              height: this.model.get('height') + 'px',
              color:  this.model.get('color'),
            }
      ));

      if( this.model.get('width') > minimum_width ) {
        // Doesn't display well on really small widths
        this.$el.html( this.redX_template( {} ) );
        this.$el.find('.markup-redx')
          .css('left', this.model.get('width')-20 );
      }
      //this.input = this.$('.edit');
      return this;
    },

    deleteMarkup: function() {
      console.log("deleteMarkup called");
      this.model.destroy();
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
      //"focusin .markup_desc" : "focusIn",
    },

    // The MarkupView listens for changes to its model, re-rendering.
    // Since there's a one-to-one correspondence between a **Markup** 
    // and a **MarkupView** in this app, we set a direct reference on 
    // the model for convenience.
    initialize: function() {
      console.log("MarkupDesc initializationz!");
      //console.log(this);
      this.model.bind('change', this.render, this);
      this.model.bind('destroy', this.remove, this);
      
    },

    // Re-render the titles of the todo item.
    render: function() {
      //this.$el.attr('style', this.template(this.model.toJSON()));
      this.$el.html( this.template(
          {
            color_name  : this.model.get('color_name') + ' area instructions:',
            desc        : this.model.get('description'),
          }
      ));

      return this;
    },

  });

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

      $(".markup_pic_container").each( function(index) {
        // Create a MarkupList on each element
        var markup_list = new MarkupList;
        markup_list.container = $(this);
        $(this).data("markup_list", markup_list);

      });

      //this.input = this.$("#new-todo");
      //this.allCheckbox = this.$("#toggle-all")[0];

      //Todos.bind('add', this.addOne, this);
      //Todos.bind('reset', this.addAll, this);
      //Todos.bind('all', this.render, this);

      //this.footer = this.$('footer');
      //this.main = $('#main');

      //Todos.fetch();
    },

    // Re-rendering the App just means refreshing the statistics -- the rest
    // of the app doesn't change.
    render: function() {
      //var done = Todos.done().length;
      //var remaining = Todos.remaining().length;

      //if (Todos.length) {
      //  this.main.show();
      //  this.footer.show();
      //  //this.footer.html(this.statsTemplate({done: done, remaining: remaining}));
      //} else {
      //  this.main.hide();
      //  this.footer.hide();
      //}

      //this.allCheckbox.checked = !remaining;
    },

    // Add a single todo item to the list by creating a view for it, and
    // appending its element to the `<ul>`.
    //addOne: function(todo) {
    //  var view = new TodoView({model: todo});
    //  this.$("#todo-list").append(view.render().el);
    //},

    // Add all items in the **Todos** collection at once.
    //addAll: function() {
    //  Todos.each(this.addOne);
    //},

    // If you hit return in the main input field, create new **Todo** model,
    // persisting it to *localStorage*.
    //createOnEnter: function(e) {
    //  if (e.keyCode != 13) return;
    //  if (!this.input.val()) return;

    //  Todos.create({title: this.input.val()});
    //  this.input.val('');
    //},
    
    createMarkup: function(e) {
      if(e.which == 1) { // left click
        var initial_size = 10;
        this.pic_container = $(e.target).parentsUntil(".markup_outer").last();
        var left = e.pageX - this.pic_container.offset().left - initial_size;
        var top = e.pageY - this.pic_container.offset().top - initial_size;

        if( ++color_index >= markup_colors.length ) {
          color_index = 0;
        }

        /* e.currentTarget would be better, but apparently Redmond doesn't
         * like it. See here: http://www.quirksmode.org/js/events_order.html */
        this.cur_markup = this.pic_container.data("markup_list").create(
            {
              /* The -6 magic here is:
               *       4px  (border width on one side
               *     + 2px  (half the border width on the other side
               *     = 6px
               *  This leaves us square in the middle of the lower right
               *  corner of our initial div size */
              left:        (left-6),
              top:         (top -6),
              height:      initial_size,
              width:       initial_size,
              color:       markup_colors[color_index]['value'],
              color_name:  markup_colors[color_index]['name'],
            }
        );
        this.cur_markup_startX = (left-6);
        this.cur_markup_startY = (top-6);
      }
    },

    resizeMarkup: function(e) {
      // Only care if we're in the middle of a move and they the left mouse is pressed
      if( this.cur_markup && e.which == 1) {
        var img = this.pic_container.find(".pic");
        var img_offset = img.offset();


        console.log( "limits: X:[", img_offset.left, "..",
                     img_offset.left + img.width(), "]   Y:[",
                     img_offset.top, "..",
                     img_offset.top  + img.height(), "]" );

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
      if( (Math.abs(x - this.cur_markup_startX) < 30) ||
          (Math.abs(y - this.cur_markup_startY) < 30) ) {
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
