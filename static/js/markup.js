// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

  if( $('#markup_app').length > 0 ) {
    // Block creation when we're clicking on little red boxes
    // uggg, this is terrible :)  polluting the global namespace
    var creationEnabled = true;
    
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
    var minimum_width = 25;

    // Our basic **Markup** model has 'left', 'top', 'width', 'height',
    // 'color', and 'description' attributes.
    var Markup = Backbone.Model.extend({

      // Default attributes for the todo item.
      defaults: function() {
        return {
          // These match directly to server side logic
        /*id:           0, -- set by server later in sync */
          left:         0,
          top:          0,
          width:        0,
          height:       0,
          color:        '#ffffff',
          color_name:   '',
          border_style: '',
          description:  '',

          // Will be set when we create the markup:
          pic_uuid:     0,
        };
      },
      
      initialize : function() {
        //console.log("I'm making me a Markup model!");
        //console.log(this);
      },

      clear: function() {
        this.destroy();
      },

    });

    //Simplistic Pic Model, only what's necessary to update the General Instructions
    var Pic = Backbone.Model.extend({

      //using the pic_handler url for saving etc
      url:  '/pic_instruction_handler/',

      //default attributes, match directly to server side logic
      defaults: function(){
        return {
          uuid:    0,
          general_instructions: '',
        };
      },

      initialize : function() {
          console.log("Creating Pic Model");
      },

      clear: function() {
        this.destroy();
      },
    
    });

    var true_sync_func = Backbone.sync;
    var CSRF_TOKEN = $('input[name=csrfmiddlewaretoken]').attr('value');
    Backbone.sync = function(method, model, options){
      options.beforeSend = function(xhr){
        xhr.setRequestHeader('X-CSRFToken', CSRF_TOKEN);
      };
      return true_sync_func( method, model, options);
    };

    // Markup Collection
    // ---------------

    // A collection of Markup elements
    var MarkupList = Backbone.Collection.extend({

      // Reference to this collection's model.
      model: Markup,

      // Url base
      url: '/markups_handler/',

      usedColors: {},
      
      initialize: function() {
        this.container = null; // Will be set to our .markup_pic_container element
        this.bind('add', this.addOne, this);
        this.bind('reset', this.addAll, this);
      },

      addOne: function(markup) {
        var view = new MarkupView( { model: markup } );
        var desc = new MarkupDesc( { model: markup } );
        this.container.append( view.render().el );
        this.container.closest('.markup_outer')
          .find('.markup_desc_container').append( desc.render().el );

        this.usedColors[ view.model.get('color_name') ] = true;
      },

      addAll: function() {
        // Start this back over
        this.usedColors = {};

        // I'd like to call a function from my current context on all the
        // elements in my collection. Here's a brief list of things that are
        // more easier:
        //   -- Eating a bologna sandwich while assaulting Jason Bourne
        //   -- Remembering how to spell 'bologna'
        var that = this;
        this.each( function(el) {
          that.addOne.call(that, el);
        });
      },

      showJustOne: function( showed ) {
        this.each( function( el ) { 
          if( el != showed.model ) {
            el.trigger('fade');
          }
          else {
            el.trigger('show');
          }
        });
      },

      showAll: function() {
        this.each( function( el ) { 
          el.trigger('show');
        });
      },

      fadeAll: function() {
        this.each( function( el ) { 
          el.trigger('fade');
        });
      },

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
        "mousedown      .markup-redx" : "deleteMarkup",
        "mouseenter     .markup-redx" : "redBoxIn",
        "mouseleave     .markup-redx" : "redBoxOut",
        //these events are on this div element itself
        "mouseenter                 " : "mouseIn",
        "mouseleave                 " : "mouseOut",
      },

      // The MarkupView listens for changes to its model, re-rendering.
      // Since there's a one-to-one correspondence between a **Markup** 
      // and a **MarkupView** in this app, we set a direct reference on 
      // the model for convenience.
      initialize: function() {
        //console.log("And, in the morning, I'm making MarkupView(s)!");
        //console.log(this);
        this.model.bind('change',  this.render,       this);
        this.model.bind('destroy', this.remove,       this);
        this.model.bind('fade',    this.fade,         this);
        this.model.bind('hide',    this.hide,         this);
        this.model.bind('show',    this.show,         this);
      },

      // Re-render the titles of the todo item.
      render: function() {
        //console.log('render: ' + this.model.get('desc_el_id'));
        //this.$el.attr('style', this.template(this.model.toJSON()));
        //console.log('MarkupView renderrrrr');
        
        //okay, admission of guilt, I feel guilty about this...
        //essentially only redraw the markup if it's size has changed
        var rebuild = false;
        var old_template = this.$el.attr('style');
        var new_template = this.template(
              {
                left:          this.model.get('left')   + 'px',
                top:           this.model.get('top')    + 'px',
                width:         this.model.get('width')  + 'px',
                height:        this.model.get('height') + 'px',
                color:         this.model.get('color'),
                border_style:  this.model.get('border_style'),
              });

        rebuild = rebuild || old_template==undefined;


        if(!rebuild)
        {
          //should I feel wrong about this?  probably...
          //find the last index of height or width, then compare the two style strings
          //for some reason even though you insert them left, top, width, height
          //the output string is left, top, height, width
          var old_idx = Math.max(old_template.indexOf("height"), old_template.indexOf("width"));
          var new_idx = Math.max(new_template.indexOf("height"), new_template.indexOf("width"));
          //move our index up to the semi colon
          var old_compare_spot = old_template.indexOf(";", old_idx + 1);
          var new_compare_spot = new_template.indexOf(";", new_idx + 1);
          //get the substring of the style string
          var old_template_sub = old_template.substring(0, old_compare_spot);
          var new_template_sub = new_template.substring(0, new_compare_spot);
          //compare, if different, redraw
          //this only occurs while resizing the markup
          //I'd love to just compare the styles, but the styles change on focus, and off focus
          rebuild = rebuild || old_template_sub!=new_template_sub;
        }

        if(rebuild)
        {
  //        console.log("rebuild: \n  old: " + old_template + "\n  new: " + new_template); 
          this.$el.attr('style', new_template);
        }

        // Doesn't display well on really small widths
        if(!readonly){
          // I just wanted to add cool hackery like Bryan does and then write a monologue about
          // how guilty I feel about doing it...  When you drag a markup really fast sometimes you get
          // lucky and the browser is like, hey why don't I hook you up and let you grab the red-x
          // image instead of continuing your markup drag... douche... So we do a slight stall in our
          // redraw of the red-x (only important in the beginning when creating, but doesn't hurt
          // anything later...
          var that = this;
          setTimeout(function(){
              that.$el.html( that.redX_template( {} ) );
              that.$el.find('.markup-redx').css('left', that.model.get('width')-20 );
            }, 50);
        }
        
        if(readonly) {
          console.log('show ' + this.model.get('color_name'));
          var title = this.model.get('color_name') + ' area instructions';
          //  attr('rel', 'popover');
          this.$el.popover(
            {
              placement :"right",
              title : title,
              content: this.model.get("description"),
              trigger: "hover",
            }
          );
        }

        return this;
      },

      deleteMarkup: function() {
        console.log("going to destroy()...");
        this.model.destroy( { wait:true } );
        // slight delay, so the click doesn't make it down to the app.
        // this works better than undelegating, and delegating
        setTimeout(function(){ creationEnabled=true; }, 10);
        console.log("destroyed!");
      },

      redBoxIn: function() {
        // console.log('red in');
        creationEnabled = false;
      },

      redBoxOut: function() {
        // console.log('red out');
        creationEnabled = true;
      },


      mouseIn: function() {
      },

      mouseOut: function() {
        if(readonly){
          // console.log('hide ' + this.model.get('color_name'));
         // this.$el.popover('hide');
        }
      },

      fade: function() {
        this.$el.css('z-index', 1);
        this.$el.css('opacity', 0.3);
      },

      hide: function() {
        this.$el.css('opacity', 0);
      },

      show: function() {
        this.$el.css('z-index', 100);
        this.$el.css('opacity', 1);
      },

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
      },

      // The MarkupView listens for changes to its model, re-rendering.
      // Since there's a one-to-one correspondence between a **Markup** 
      // and a **MarkupView** in this app, we set a direct reference on 
      // the model for convenience.
      initialize: function() {
        //console.log("MarkupDesc initializationz!");
        //console.log(this);
        this.model.bind('change',  this.render,       this);
        this.model.bind('destroy', this.remove,       this);
        this.model.bind('hide',    this.hide,         this);
        this.model.bind('focus',   this.force_focus,  this);
      },

      // Re-render the titles of the todo item.
      render: function() {
        //this.$el.attr('style', this.template(this.model.toJSON()));
        //only render this html once
        //no need to recreate after it's been built
        if(this.$el.context.innerHTML == "")
        {
          this.$el.html( this.template(
            {
              color         : this.model.get('color'),
              color_name    : this.model.get('color_name') + ' area instructions:',
              border_style  : this.model.get('border_style'),
              desc          : this.model.get('description'),
              readonly:      '',
            }
          ));
          this.$el.find('.desc').each(function(){ joinAutoSize(this); });
        }

        return this;
      },

      focusIn : function() {
        console.log("focusIn " + this.model.get('color_name'));

        App.fadeAllMarkups();
        this.$el.closest('.markup_outer').data('markup_list')
          .showJustOne( this );
      },

      focusOut : function() {
        console.log("focusOut");
        //console.log(this.$el.find('.desc').val());

        //only save when the description has changed
        var desc = this.$el.find('.desc').val(); 
        if( desc != this.model.get('description')){
          console.log("save description " + desc);
          this.model.save( { 'description' : desc }, { wait : true } );
        }

        // Show all the elements again
        App.showAllMarkups();
      },

      force_focus: function() {
        var desc = this.$el.find('.desc');
        desc.focus();
      },


      hide : function() {
        this.$el.hide();
      }

    });

    var GeneralInstructionView = Backbone.View.extend({

      //using the Pic model
      model: Pic,


      initialize: function() {
          console.log('created a wicked awesome Instruction view: ' + this.model.get('pic_uuid'));
          
      },

      events: {
       "focusout   .desc" : "focusOut",

      },

      render: function(){
  //      console.log("render the wicked awesome");  
      },

      focusOut: function(){
        var instruction = this.$el.find('.desc').val();
        console.log("Got focusOut for general instruction value: " + instruction);
        if( instruction != this.model.get('general_instructions') ) {
          this.model.save({ 'general_instructions': instruction } , 
                          { wait : true });
        }
      }
      


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
        //"mouseleave .markup_pic_container" : "mouseLeft",
      },

      // At initialization we bind to the relevant events on the `Todos`
      // collection, when items are added or changed. Kick things off by
      // loading any preexisting todos that might be saved in *localStorage*.
      initialize: function() {

        //console.log("AppView init");

        $(".markup_outer").each( function() {
          // Create a MarkupList on each element
          var markup_list = new MarkupList;
          // Give markup_list a pointer to his container element,
          // and give the container element a pointer to his markuplist.
          markup_list.container = $(this).find(".markup_pic_container");
          $(this).data("markup_list", markup_list);

          var general_instructions = $(this).find(".desc").val() ;
          var pic_model = new Pic( {uuid: markup_list.container.attr('uuid'),
                                    general_instructions: general_instructions } );
          
          var instruction = $(this).find(".instruction");

          new GeneralInstructionView( { el : instruction, model: pic_model } );
          markup_list.reset( jQuery.parseJSON( $(this).find('.preloaded_markups').html() ) );
        });
        

      },

      fadeAllMarkups: function() {
        $(".markup_outer").each( function() {
          $(this).data("markup_list").fadeAll();
        });
      },
      
      showAllMarkups: function() {
        $(".markup_outer").each( function() {
          $(this).data("markup_list").showAll();
        });
      },


      // Re-rendering the App just means refreshing the statistics -- the rest
      // of the app doesn't change.
      render: function() {
          console.log('render app view');
      },

      createMarkup: function(e) {
        console.log('create');
        if(e.which == 1 && creationEnabled) { // left click
        console.log('serious create');
          var initial_size = 10;
          /* This seems like a lot of work, but e.target seems a little bit
           * unpredictable, so I'm dancing around to ensure that I always end
           * up at my desired .markup_pic_container element */

          /* e.currentTarget would be better, but apparently Redmond doesn't
           * like it. See here: http://www.quirksmode.org/js/events_order.html */
          this.pic_container = $(e.target).closest('.markup_outer')
            .find(".markup_pic_container");
          var left = e.pageX - this.pic_container.offset().left - initial_size;
          var top = e.pageY - this.pic_container.offset().top - initial_size;

          var color_index = 0;
          var markup_list = this.pic_container.parent().data("markup_list");

          while( color_index < markup_colors.length &&
                 markup_colors[color_index]['name'] in markup_list.usedColors )
          {
            color_index++;
          }

          if( color_index == markup_colors.length ) {
            console.log('Out of unique colors! Abort!');
            return;
          }


          markup_list.usedColors[ markup_colors[color_index]['name'] ] = true;

          this.cur_markup = markup_list.create(
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
                pic_uuid:      this.pic_container.attr('uuid'),
              }
          );

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
        //console.log('finish w/o pic_container');
        if (this.pic_container == null)
          return;
        console.log('finish w pic_container');

        var x = e.pageX - this.pic_container.offset().left;
        var y = e.pageY - this.pic_container.offset().top;

        // If the markup is too small, get rid of it
        if( (Math.abs(x - this.cur_markup_startX) < minimum_width) ||
            (Math.abs(y - this.cur_markup_startY) < minimum_width) ) {

            /*
             * Some weird hackery in here. Basically, we want to destroy
             * this.cur_markup, but we've probably got a create() request to
             * server already in flight. If we destroy it *before* that create()
             * finishes, we'll destroy it client side without destroying it
             * server side. (We won't don't yet know the id to destroy it on
             * the server.) That means it'll still be created on the server and
             * it'll show up on page reloads.
             *
             * Solution? Don't destroy until our create() is done
             */

            // Let's at least hide it from the user in the mean time
            this.cur_markup.trigger('hide');

            var destroy_func = function(that) {
              if(that.cur_markup==null)
                return;

              var markup_id = that.cur_markup.get('id');
              if(markup_id) {
                /* Has an 'id', so it has been synced to the server, so
                 * we can delete it now. */
                that.cur_markup.destroy( { wait : true } );
                console.log('Small markup ' + that.cur_markup.get('color_name') + ' ' + markup_id + ' has been destroyed');

                that.cur_markup = null;
                that.cur_markup_startX = null;
                that.cur_markup_startY = null;
                that.pic_container = null;
              }
              else {
                /* Does not have an 'id', so our create() request hasn't gone through
                 * for this object. We can't safely destroy it until the creation has
                 * gone through. */
                console.log('Small markup not yet created -- delaying...');
                setTimeout(destroy_func, 20, that);
              }
            }

            setTimeout(destroy_func, 20, this);
            //this.cur_markup.destroy( { wait : true } );

            var markup_list = this.pic_container.parent().data("markup_list");
            var color_name = this.cur_markup.get('color_name');
            delete markup_list.usedColors[ color_name ];
        }
        else if (this.cur_markup) {
          // This guy is big enough! Let's sync() to the server
          console.log('save');
          this.cur_markup.save();
          this.cur_markup.trigger('focus');
          //if the mouse was hovering over redx when we moved focus
          creationEnabled = true;

          this.cur_markup = null;
          this.cur_markup_startX = null;
          this.cur_markup_startY = null;
          this.pic_container = null;
        }
      },

      /*mouseLeft: function(e){
        //console.log('tricky tricky, you left!!! ' + e.which );

      },*/

    });

    // Finally, we kick things off by creating the **App**.
    var App = new AppView;

    //Auto submit form when they've chosen a file
    $('#doc_file').change(doc_upload);

    function doc_upload() {
      //call submit first, or screwing with the view breaks the upload
      $('form').submit();
      var button = $('#doc_file');
      var parent = button.parent();
      parent.addClass('disabled');
      parent.text('Busy Uploading...');
      button.css('cursor', 'default');
      button.attr('disabled', 'disabled');
    }

    //lets do some readonly stuff (this value is set in the template)
    if(readonly)
    {
      $('.desc').each(function(){$(this).attr('readonly','readonly')});
      App.undelegateEvents();
    }
    
    //fun arrow keys to shift from one page to the next
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
  }
});

