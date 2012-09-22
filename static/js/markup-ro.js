// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){
  
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

    // The DOM events specific to an item.
    events: {
      // This event needs to be mousedown instead of click, because otherwise
      // when we depress the mouse, we'll find ourselves in the middle of 
      // creating a new markup rather than deleting this one. (mousedown 
      // is caught by the markup_pic_container)
    },

    // The MarkupView listens for changes to its model, re-rendering.
    // Since there's a one-to-one correspondence between a **Markup** 
    // and a **MarkupView** in this app, we set a direct reference on 
    // the model for convenience.
    initialize: function() {
      //console.log("And, in the morning, I'm making MarkupView(s)!");
      //console.log(this);
      this.model.bind('change',  this.render, this);
      this.model.bind('fade',    this.fade,   this);
      this.model.bind('hide',    this.hide,   this);
      this.model.bind('show',    this.show,   this);
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
      return this;
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
    },

    // The MarkupView listens for changes to its model, re-rendering.
    // Since there's a one-to-one correspondence between a **Markup** 
    // and a **MarkupView** in this app, we set a direct reference on 
    // the model for convenience.
    initialize: function() {
      //console.log("MarkupDesc initializationz!");
      //console.log(this);
      this.model.bind('change',  this.render, this);
      this.model.bind('hide',    this.hide,   this);
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
            readonly      : 'readonly',
          }
        ));
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
        console.log("don't save description " + desc);
      }

      // Show all the elements again
      App.showAllMarkups();
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

  });

  // Finally, we kick things off by creating the **App**.
  var App = new AppView;

  //temporary job creation
  var FakeJobView = Backbone.View.extend({

    el: $("#fake_job_app"),

    // Delegated events for creating new items, and clearing completed ones.
        events: {
            //"keypress #new-todo":  "createOnEnter",
            "click  a#FakeJobGen" : "createJob",
            //"mouseleave .markup_pic_container" : "finishMarkup",
        },

        createJob: function(){
            try
  {
    $.ajax({
      type: 'POST',
      url: '/kill_job/',
      data: '',
      success : function(data, textStatus) {
        console.log("TODO: REMOVE ME");
        console.log(data);
        console.log(textStatus);
        location.reload(true);
      }
    });
  }
  catch(Err)
  {
      console.log("error: " + Err);
  }
        return false;
        },
      });
 var fjv = new FakeJobView();
});
